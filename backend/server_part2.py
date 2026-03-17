# ============================================================================
# QUESTS SYSTEM
# ============================================================================

@app.get("/api/game/quests/available")
async def get_available_quests(current_user: dict = Depends(get_current_user)):
    """Get available quests"""
    # Check active quest
    active = await db.user_quests.find_one({'user_id': current_user['id'], 'status': 'active'}, {'_id': 0})
    
    # Get completed (non-repeatable) quests
    completed_non_repeat = await db.user_quests.find(
        {'user_id': current_user['id'], 'status': 'completed'},
        {'quest_id': 1}
    ).to_list(100)
    completed_ids = [q['quest_id'] for q in completed_non_repeat]
    
    # Filter available
    available = []
    for quest in MASTER_QUESTS:
        # Check level
        if current_user['level'] < quest['min_level']:
            continue
        # Check if already completed (and not repeatable)
        if not quest.get('repeatable', False) and quest['id'] in completed_ids:
            continue
        available.append(quest)
    
    return {
        'active_quest': serialize_doc(active),
        'available_quests': available
    }

@app.post("/api/game/quests/accept")
async def accept_quest(req: QuestRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    # Check if already on quest
    active = await db.user_quests.find_one({'user_id': user_id, 'status': 'active'})
    if active:
        raise HTTPException(status_code=400, detail="Du hast bereits eine aktive Quest")
    
    # Find quest
    quest = next((q for q in MASTER_QUESTS if q['id'] == req.quest_id), None)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest nicht gefunden")
    
    if current_user['level'] < quest['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {quest['min_level']} erforderlich")
    
    # Check energy
    current_energy = await regenerate_energy(current_user)
    if current_energy < quest['energy_cost']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {quest['energy_cost']})")
    
    # Deduct energy
    await db.users.update_one(
        {'id': user_id},
        {'$inc': {'energy': -quest['energy_cost']}, '$set': {'last_energy_regen': datetime.now(timezone.utc)}}
    )
    
    # Create user quest
    complete_time = datetime.now(timezone.utc) + timedelta(minutes=quest['duration_minutes'])
    user_quest = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'quest_id': req.quest_id,
        'quest_name': quest['name'],
        'start_time': datetime.now(timezone.utc),
        'complete_time': complete_time,
        'status': 'active'
    }
    await db.user_quests.insert_one(user_quest)
    
    return {
        'success': True,
        'message': f'Quest "{quest["name"]}" akzeptiert!',
        'complete_time': complete_time.isoformat(),
        'duration_minutes': quest['duration_minutes']
    }

@app.post("/api/game/quests/complete")
async def complete_quest(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    
    user_quest = await db.user_quests.find_one({'user_id': user_id, 'status': 'active'})
    if not user_quest:
        raise HTTPException(status_code=404, detail="Keine aktive Quest")
    
    complete_time = user_quest['complete_time']
    if isinstance(complete_time, str):
        complete_time = datetime.fromisoformat(complete_time.replace('Z', '+00:00'))
    
    if datetime.now(timezone.utc) < complete_time:
        remaining = int((complete_time - datetime.now(timezone.utc)).total_seconds() / 60)
        raise HTTPException(status_code=400, detail=f"Quest noch nicht abgeschlossen ({remaining} Min verbleibend)")
    
    # Find quest
    quest = next((q for q in MASTER_QUESTS if q['id'] == user_quest['quest_id']), None)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest Daten nicht gefunden")
    
    # Rewards
    gold_reward = quest['rewards']['gold']
    xp_reward = quest['rewards']['xp']
    
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': gold_reward, 'xp': xp_reward}})
    
    # Mark completed
    await db.user_quests.update_one(
        {'id': user_quest['id']},
        {'$set': {'status': 'completed', 'completed_at': datetime.now(timezone.utc)}}
    )
    
    # Item reward
    item_reward = None
    if 'item' in quest['rewards']:
        item_id = quest['rewards']['item']
        existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
        if existing:
            await db.inventories.update_one({'user_id': user_id, 'item_id': item_id}, {'$inc': {'quantity': 1}})
        else:
            await db.inventories.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'item_id': item_id,
                'quantity': 1,
                'acquired_at': datetime.now(timezone.utc)
            })
        
        item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
        item_reward = item_data['name'] if item_data else item_id
    
    # Level up check
    updated_user = await db.users.find_one({'id': user_id})
    new_level = calculate_level(updated_user['xp'])
    level_up = new_level > updated_user['level']
    if level_up:
        await db.users.update_one({'id': user_id}, {'$set': {'level': new_level}})
        await log_event('quest', f'{current_user["username"]} reached level {new_level}!', user_id)
    
    await log_event('quest', f'{current_user["username"]} completed quest: {quest["name"]}', user_id)
    
    message = f'Quest abgeschlossen! +{gold_reward} Gold, +{xp_reward} XP'
    if item_reward:
        message += f', +1 {item_reward}'
    
    return {
        'success': True,
        'message': message,
        'rewards': {'gold': gold_reward, 'xp': xp_reward, 'item': item_reward},
        'level_up': level_up,
        'new_level': new_level if level_up else None
    }

# ============================================================================
# INVENTORY SYSTEM
# ============================================================================

@app.get("/api/game/inventory")
async def get_inventory(current_user: dict = Depends(get_current_user)):
    """Get inventory"""
    inv_items = await db.inventories.find({'user_id': current_user['id']}, {'_id': 0}).to_list(200)
    
    enriched = []
    for inv_item in inv_items:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == inv_item['item_id']), None)
        if item_data:
            enriched.append({**inv_item, 'item_details': item_data})
    
    return {
        'inventory': serialize_doc(enriched),
        'equipped': current_user.get('equipment', {})
    }

@app.post("/api/game/inventory/use")
async def use_item(req: UseItemRequest, current_user: dict = Depends(get_current_user)):
    """Use consumable"""
    user_id = current_user['id']
    
    inv_item = await db.inventories.find_one({'user_id': user_id, 'item_id': req.item_id})
    if not inv_item or inv_item['quantity'] < 1:
        raise HTTPException(status_code=404, detail="Item nicht im Inventar")
    
    item_data = next((i for i in MASTER_ITEMS if i['id'] == req.item_id), None)
    if not item_data or item_data['type'] != 'consumable':
        raise HTTPException(status_code=400, detail="Dieser Gegenstand kann nicht benutzt werden")
    
    # Apply effects
    effect = item_data.get('effect', {})
    updates = {}
    messages = []
    
    if 'hp' in effect:
        current_hp = await regenerate_hp(current_user)
        new_hp = min(MAX_HP, current_hp + effect['hp'])
        updates['hp'] = new_hp
        messages.append(f"+{effect['hp']} HP")
    
    if 'energy' in effect:
        current_energy = await regenerate_energy(current_user)
        new_energy = min(MAX_ENERGY, current_energy + effect['energy'])
        updates['energy'] = new_energy
        messages.append(f"+{effect['energy']} Energie")
    
    if updates:
        await db.users.update_one({'id': user_id}, {'$set': updates})
    
    # Remove from inventory
    if inv_item['quantity'] == 1:
        await db.inventories.delete_one({'id': inv_item['id']})
    else:
        await db.inventories.update_one({'id': inv_item['id']}, {'$inc': {'quantity': -1}})
    
    return {
        'success': True,
        'message': f'{item_data["name"]} benutzt: {", ".join(messages)}',
        'effects': effect
    }

@app.post("/api/game/inventory/equip")
async def equip_item(req: EquipItemRequest, current_user: dict = Depends(get_current_user)):
    """Equip item"""
    user_id = current_user['id']
    
    # Check if in inventory
    inv_item = await db.inventories.find_one({'user_id': user_id, 'item_id': req.item_id})
    if not inv_item:
        raise HTTPException(status_code=404, detail="Item nicht im Inventar")
    
    item_data = next((i for i in MASTER_ITEMS if i['id'] == req.item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Item Daten nicht gefunden")
    
    # Check if equipable
    if item_data.get('slot') != req.slot:
        raise HTTPException(status_code=400, detail=f"Dieser Gegenstand gehört in Slot: {item_data.get('slot', 'none')}")
    
    # Unequip current item in slot (return to inventory)
    current_equipment = current_user.get('equipment', {})
    old_item_id = current_equipment.get(req.slot)
    
    if old_item_id:
        existing_inv = await db.inventories.find_one({'user_id': user_id, 'item_id': old_item_id})
        if existing_inv:
            await db.inventories.update_one({'user_id': user_id, 'item_id': old_item_id}, {'$inc': {'quantity': 1}})
        else:
            await db.inventories.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'item_id': old_item_id,
                'quantity': 1,
                'acquired_at': datetime.now(timezone.utc)
            })
    
    # Remove new item from inventory
    if inv_item['quantity'] == 1:
        await db.inventories.delete_one({'id': inv_item['id']})
    else:
        await db.inventories.update_one({'id': inv_item['id']}, {'$inc': {'quantity': -1}})
    
    # Equip
    await db.users.update_one(
        {'id': user_id},
        {'$set': {f'equipment.{req.slot}': req.item_id}}
    )
    
    return {
        'success': True,
        'message': f'{item_data["name"]} ausgerüstet'
    }

@app.post("/api/game/inventory/unequip")
async def unequip_item(slot: str, current_user: dict = Depends(get_current_user)):
    """Unequip item from slot"""
    user_id = current_user['id']
    
    equipment = current_user.get('equipment', {})
    item_id = equipment.get(slot)
    
    if not item_id:
        raise HTTPException(status_code=400, detail="Kein Gegenstand in diesem Slot")
    
    # Return to inventory
    existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
    if existing:
        await db.inventories.update_one({'user_id': user_id, 'item_id': item_id}, {'$inc': {'quantity': 1}})
    else:
        await db.inventories.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'item_id': item_id,
            'quantity': 1,
            'acquired_at': datetime.now(timezone.utc)
        })
    
    # Unequip
    await db.users.update_one({'id': user_id}, {'$set': {f'equipment.{slot}': None}})
    
    return {'success': True, 'message': 'Gegenstand abgelegt'}

# ============================================================================
# SHOP SYSTEM
# ============================================================================

@app.get("/api/game/shop/items")
async def get_shop_items(current_user: dict = Depends(get_current_user)):
    """Get shop inventory"""
    available = [item for item in MASTER_ITEMS if item['required_level'] <= current_user['level']]
    return available

@app.post("/api/game/shop/buy")
async def buy_from_shop(item_id: str, quantity: int = 1, current_user: dict = Depends(get_current_user)):
    """Buy from shop"""
    user_id = current_user['id']
    
    item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Gegenstand nicht gefunden")
    
    if current_user['level'] < item_data['required_level']:
        raise HTTPException(status_code=400, detail=f"Level {item_data['required_level']} erforderlich")
    
    total_cost = item_data['price'] * quantity
    if current_user['gold'] < total_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {total_cost})")
    
    # Deduct gold
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -total_cost}})
    
    # Add to inventory
    existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
    if existing:
        await db.inventories.update_one({'user_id': user_id, 'item_id': item_id}, {'$inc': {'quantity': quantity}})
    else:
        await db.inventories.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'item_id': item_id,
            'quantity': quantity,
            'acquired_at': datetime.now(timezone.utc)
        })
    
    return {
        'success': True,
        'message': f'{quantity}x {item_data["name"]} gekauft für {total_cost} Gold',
        'cost': total_cost
    }

# ============================================================================
# MARKET SYSTEM
# ============================================================================

@app.get("/api/game/market/listings")
async def get_market_listings(item_type: Optional[str] = None, limit: int = 50):
    """Get market listings"""
    query = {'active': True}
    if item_type:
        query['item_type'] = item_type
    
    listings = await db.market_listings.find(query, {'_id': 0}).sort('created_at', -1).limit(limit).to_list(limit)
    
    # Enrich
    enriched = []
    for listing in listings:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == listing['item_id']), None)
        seller = await db.users.find_one({'id': listing['seller_id']}, {'username': 1, 'level': 1})
        
        enriched.append({
            **serialize_doc(listing),
            'item_details': item_data,
            'seller_name': seller['username'] if seller else 'Unknown',
            'seller_level': seller['level'] if seller else 1
        })
    
    return enriched

@app.post("/api/game/market/create")
async def create_market_listing(req: MarketListingCreate, current_user: dict = Depends(get_current_user)):
    """Create market listing"""
    user_id = current_user['id']
    
    inv_item = await db.inventories.find_one({'user_id': user_id, 'item_id': req.item_id})
    if not inv_item or inv_item['quantity'] < req.quantity:
        raise HTTPException(status_code=400, detail="Nicht genug Gegenstände im Inventar")
    
    item_data = next((i for i in MASTER_ITEMS if i['id'] == req.item_id), None)
    if not item_data:
        raise HTTPException(status_code=404, detail="Gegenstand nicht gefunden")
    
    # Remove from inventory
    if inv_item['quantity'] == req.quantity:
        await db.inventories.delete_one({'id': inv_item['id']})
    else:
        await db.inventories.update_one({'id': inv_item['id']}, {'$inc': {'quantity': -req.quantity}})
    
    # Create listing
    listing = {
        'id': str(uuid.uuid4()),
        'seller_id': user_id,
        'item_id': req.item_id,
        'item_name': item_data['name'],
        'item_type': item_data['type'],
        'quantity': req.quantity,
        'price_per_unit': req.price_per_unit,
        'total_price': req.price_per_unit * req.quantity,
        'active': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.market_listings.insert_one(listing)
    
    return {
        'success': True,
        'message': f'Angebot erstellt: {req.quantity}x {item_data["name"]} für {listing["total_price"]} Gold',
        'listing_id': listing['id']
    }

@app.post("/api/game/market/buy")
async def buy_from_market(req: MarketBuyRequest, current_user: dict = Depends(get_current_user)):
    """Buy from market"""
    user_id = current_user['id']
    
    listing = await db.market_listings.find_one({'id': req.listing_id, 'active': True})
    if not listing:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    if listing['seller_id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst nicht von dir selbst kaufen")
    
    if req.quantity > listing['quantity']:
        raise HTTPException(status_code=400, detail="Nicht genug verfügbar")
    
    total_cost = req.quantity * listing['price_per_unit']
    if current_user['gold'] < total_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {total_cost})")
    
    # Transfer gold
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -total_cost}})
    await db.users.update_one({'id': listing['seller_id']}, {'$inc': {'gold': total_cost}})
    
    # Add to buyer inventory
    existing = await db.inventories.find_one({'user_id': user_id, 'item_id': listing['item_id']})
    if existing:
        await db.inventories.update_one({'user_id': user_id, 'item_id': listing['item_id']}, {'$inc': {'quantity': req.quantity}})
    else:
        await db.inventories.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'item_id': listing['item_id'],
            'quantity': req.quantity,
            'acquired_at': datetime.now(timezone.utc)
        })
    
    # Update listing
    if req.quantity == listing['quantity']:
        await db.market_listings.update_one({'id': req.listing_id}, {'$set': {'active': False}})
    else:
        await db.market_listings.update_one(
            {'id': req.listing_id},
            {
                '$inc': {'quantity': -req.quantity},
                '$set': {'total_price': (listing['quantity'] - req.quantity) * listing['price_per_unit']}
            }
        )
    
    # Check merchant achievement
    total_trade_value = await db.market_listings.aggregate([
        {'$match': {'seller_id': user_id, 'active': False}},
        {'$group': {'_id': None, 'total': {'$sum': '$total_price'}}}
    ]).to_list(1)
    
    if total_trade_value and total_trade_value[0]['total'] >= 1000:
        await check_and_award_achievement(user_id, 'merchant')
    
    return {
        'success': True,
        'message': f'{req.quantity}x {listing["item_name"]} gekauft für {total_cost} Gold',
        'cost': total_cost
    }

@app.get("/api/game/market/my-listings")
async def get_my_listings(current_user: dict = Depends(get_current_user)):
    """Get own listings"""
    listings = await db.market_listings.find(
        {'seller_id': current_user['id'], 'active': True},
        {'_id': 0}
    ).to_list(100)
    
    enriched = []
    for listing in listings:
        item_data = next((i for i in MASTER_ITEMS if i['id'] == listing['item_id']), None)
        enriched.append({**serialize_doc(listing), 'item_details': item_data})
    
    return enriched

@app.delete("/api/game/market/cancel/{listing_id}")
async def cancel_listing(listing_id: str, current_user: dict = Depends(get_current_user)):
    """Cancel listing"""
    listing = await db.market_listings.find_one({'id': listing_id, 'seller_id': current_user['id'], 'active': True})
    if not listing:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    # Return items
    existing = await db.inventories.find_one({'user_id': current_user['id'], 'item_id': listing['item_id']})
    if existing:
        await db.inventories.update_one({'user_id': current_user['id'], 'item_id': listing['item_id']}, {'$inc': {'quantity': listing['quantity']}})
    else:
        await db.inventories.insert_one({
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'item_id': listing['item_id'],
            'quantity': listing['quantity'],
            'acquired_at': datetime.now(timezone.utc)
        })
    
    await db.market_listings.update_one({'id': listing_id}, {'$set': {'active': False}})
    
    return {'success': True, 'message': f'{listing["quantity"]}x {listing["item_name"]} zurück im Inventar'}

# ============================================================================
# BANKING SYSTEM (Treasury + Bank)
# ============================================================================

@app.get("/api/game/bank/account")
async def get_bank_account(current_user: dict = Depends(get_current_user)):
    """Get bank account"""
    account = await db.bank_accounts.find_one({'user_id': current_user['id']}, {'_id': 0})
    if not account:
        account = {
            'id': str(uuid.uuid4()),
            'user_id': current_user['id'],
            'balance': 0,
            'created_at': datetime.now(timezone.utc)
        }
        await db.bank_accounts.insert_one(account)
    
    return serialize_doc(account)

@app.post("/api/game/bank/deposit")
async def bank_deposit(req: BankDepositRequest, current_user: dict = Depends(get_current_user)):
    """Deposit to bank"""
    user_id = current_user['id']
    
    if current_user['gold'] < req.amount:
        raise HTTPException(status_code=400, detail="Nicht genug Gold")
    
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -req.amount}})
    await db.bank_accounts.update_one(
        {'user_id': user_id},
        {'$inc': {'balance': req.amount}},
        upsert=True
    )
    
    return {'success': True, 'message': f'{req.amount} Gold eingezahlt'}

@app.post("/api/game/bank/withdraw")
async def bank_withdraw(req: BankWithdrawRequest, current_user: dict = Depends(get_current_user)):
    """Withdraw from bank"""
    user_id = current_user['id']
    
    account = await db.bank_accounts.find_one({'user_id': user_id})
    if not account or account['balance'] < req.amount:
        raise HTTPException(status_code=400, detail="Nicht genug Gold auf dem Bankkonto")
    
    await db.bank_accounts.update_one({'user_id': user_id}, {'$inc': {'balance': -req.amount}})
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': req.amount}})
    
    # Check rich achievement
    updated_user = await db.users.find_one({'id': user_id})
    if updated_user['gold'] >= 10000:
        await check_and_award_achievement(user_id, 'rich')
    
    return {'success': True, 'message': f'{req.amount} Gold abgehoben'}

# ============================================================================
# GUILDS SYSTEM
# ============================================================================

@app.get("/api/game/guilds")
async def get_guilds(limit: int = 50):
    """Get list of guilds"""
    guilds = await db.guilds.find({}, {'_id': 0}).sort('member_count', -1).limit(limit).to_list(limit)
    return serialize_doc(guilds)

@app.post("/api/game/guilds/create")
async def create_guild(req: GuildCreateRequest, current_user: dict = Depends(get_current_user)):
    """Create guild"""
    user_id = current_user['id']
    
    # Check if already in guild
    existing_membership = await db.guild_members.find_one({'user_id': user_id})
    if existing_membership:
        raise HTTPException(status_code=400, detail="Du bist bereits Mitglied einer Gilde")
    
    # Check name uniqueness
    existing_guild = await db.guilds.find_one({'name': req.name})
    if existing_guild:
        raise HTTPException(status_code=400, detail="Gildenname bereits vergeben")
    
    # Cost to create
    creation_cost = 5000
    if current_user['gold'] < creation_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {creation_cost})")
    
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -creation_cost}})
    
    # Create guild
    guild_id = str(uuid.uuid4())
    guild = {
        'id': guild_id,
        'name': req.name,
        'description': req.description,
        'leader_id': user_id,
        'leader_name': current_user['username'],
        'member_count': 1,
        'created_at': datetime.now(timezone.utc)
    }
    await db.guilds.insert_one(guild)
    
    # Add member
    await db.guild_members.insert_one({
        'id': str(uuid.uuid4()),
        'guild_id': guild_id,
        'user_id': user_id,
        'username': current_user['username'],
        'role': 'leader',
        'joined_at': datetime.now(timezone.utc)
    })
    
    await log_event('guild', f'{current_user["username"]} founded guild: {req.name}', user_id)
    await check_and_award_achievement(user_id, 'guild_master')
    
    return {
        'success': True,
        'message': f'Gilde "{req.name}" gegründet!',
        'guild_id': guild_id
    }

@app.post("/api/game/guilds/{guild_id}/join")
async def join_guild(guild_id: str, current_user: dict = Depends(get_current_user)):
    """Join guild"""
    user_id = current_user['id']
    
    # Check if already in guild
    existing_membership = await db.guild_members.find_one({'user_id': user_id})
    if existing_membership:
        raise HTTPException(status_code=400, detail="Du bist bereits Mitglied einer Gilde")
    
    # Find guild
    guild = await db.guilds.find_one({'id': guild_id})
    if not guild:
        raise HTTPException(status_code=404, detail="Gilde nicht gefunden")
    
    # Add member
    await db.guild_members.insert_one({
        'id': str(uuid.uuid4()),
        'guild_id': guild_id,
        'user_id': user_id,
        'username': current_user['username'],
        'role': 'member',
        'joined_at': datetime.now(timezone.utc)
    })
    
    # Update count
    await db.guilds.update_one({'id': guild_id}, {'$inc': {'member_count': 1}})
    
    await log_event('guild', f'{current_user["username"]} joined guild: {guild["name"]}', user_id)
    
    return {'success': True, 'message': f'Du bist der Gilde "{guild["name"]}" beigetreten!'}

@app.get("/api/game/guilds/my-guild")
async def get_my_guild(current_user: dict = Depends(get_current_user)):
    """Get user's guild"""
    membership = await db.guild_members.find_one({'user_id': current_user['id']}, {'_id': 0})
    if not membership:
        return None
    
    guild = await db.guilds.find_one({'id': membership['guild_id']}, {'_id': 0})
    members = await db.guild_members.find({'guild_id': membership['guild_id']}, {'_id': 0}).to_list(100)
    
    return {
        'guild': serialize_doc(guild),
        'my_role': membership['role'],
        'members': serialize_doc(members)
    }

@app.post("/api/game/guilds/leave")
async def leave_guild(current_user: dict = Depends(get_current_user)):
    """Leave guild"""
    user_id = current_user['id']
    
    membership = await db.guild_members.find_one({'user_id': user_id})
    if not membership:
        raise HTTPException(status_code=400, detail="Du bist in keiner Gilde")
    
    if membership['role'] == 'leader':
        raise HTTPException(status_code=400, detail="Der Gildenführer kann nicht einfach gehen. Übergib die Führung oder löse die Gilde auf.")
    
    guild = await db.guilds.find_one({'id': membership['guild_id']})
    
    await db.guild_members.delete_one({'id': membership['id']})
    await db.guilds.update_one({'id': membership['guild_id']}, {'$inc': {'member_count': -1}})
    
    return {'success': True, 'message': f'Du hast die Gilde "{guild["name"]}" verlassen'}

# ============================================================================
# TAVERN GAMBLING
# ============================================================================

@app.post("/api/game/tavern/dice")
async def play_dice(req: DiceGameRequest, current_user: dict = Depends(get_current_user)):
    """Play dice game"""
    user_id = current_user['id']
    
    if current_user['gold'] < req.wager:
        raise HTTPException(status_code=400, detail="Nicht genug Gold für diesen Einsatz")
    
    # Deduct wager
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -req.wager}})
    
    # Roll 6 dice
    rolls = [random.randint(1, 6) for _ in range(6)]
    total = sum(rolls)
    
    # Win condition: total >= 21 (generous)
    won = total >= 21
    
    if won:
        winnings = req.wager * 2
        await db.users.update_one({'id': user_id}, {'$inc': {'gold': winnings}})
        
        return {
            'success': True,
            'won': True,
            'message': f'Gewonnen! {winnings} Gold',
            'rolls': rolls,
            'total': total,
            'winnings': winnings,
            'net_profit': winnings - req.wager
        }
    else:
        return {
            'success': True,
            'won': False,
            'message': f'Verloren! {req.wager} Gold verloren',
            'rolls': rolls,
            'total': total,
            'net_profit': -req.wager
        }

# ============================================================================
# EXPLORATION & HUNTING
# ============================================================================

@app.post("/api/game/travel")
async def travel_to_kingdom(req: TravelRequest, current_user: dict = Depends(get_current_user)):
    """Travel to another kingdom"""
    user_id = current_user['id']
    
    # Check if already traveling
    existing = await db.travel_sessions.find_one({'user_id': user_id, 'completed': False})
    if existing:
        raise HTTPException(status_code=400, detail="Du reist bereits")
    
    # Find kingdom
    kingdom = next((k for k in KINGDOMS if k['id'] == req.kingdom_id), None)
    if not kingdom:
        raise HTTPException(status_code=404, detail="Königreich nicht gefunden")
    
    if current_user['location'] == req.kingdom_id:
        raise HTTPException(status_code=400, detail="Du bist bereits hier")
    
    # Travel cost and duration
    travel_cost = 50
    travel_duration = 30  # minutes
    
    current_energy = await regenerate_energy(current_user)
    if current_energy < 15:
        raise HTTPException(status_code=400, detail="Nicht genug Energie zum Reisen (benötigt: 15)")
    
    if current_user['gold'] < travel_cost:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {travel_cost})")
    
    # Deduct costs
    await db.users.update_one(
        {'id': user_id},
        {
            '$inc': {'gold': -travel_cost, 'energy': -15},
            '$set': {'last_energy_regen': datetime.now(timezone.utc)}
        }
    )
    
    # Create travel session
    arrival_time = datetime.now(timezone.utc) + timedelta(minutes=travel_duration)
    await db.travel_sessions.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'from_kingdom': current_user['location'],
        'to_kingdom': req.kingdom_id,
        'destination_name': kingdom['name'],
        'start_time': datetime.now(timezone.utc),
        'arrival_time': arrival_time,
        'completed': False
    })
    
    return {
        'success': True,
        'message': f'Reise nach {kingdom["name"]} begonnen',
        'arrival_time': arrival_time.isoformat(),
        'duration_minutes': travel_duration
    }

@app.post("/api/game/travel/complete")
async def complete_travel(current_user: dict = Depends(get_current_user)):
    """Complete travel"""
    user_id = current_user['id']
    
    travel = await db.travel_sessions.find_one({'user_id': user_id, 'completed': False})
    if not travel:
        raise HTTPException(status_code=404, detail="Keine aktive Reise")
    
    arrival_time = travel['arrival_time']
    if isinstance(arrival_time, str):
        arrival_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
    
    if datetime.now(timezone.utc) < arrival_time:
        raise HTTPException(status_code=400, detail="Reise noch nicht abgeschlossen")
    
    # Update location
    await db.users.update_one({'id': user_id}, {'$set': {'location': travel['to_kingdom']}})
    await db.travel_sessions.update_one({'id': travel['id']}, {'$set': {'completed': True}})
    
    return {
        'success': True,
        'message': f'Ankunft in {travel["destination_name"]}!'
    }

@app.get("/api/game/hunting/creatures")
async def get_creatures(current_user: dict = Depends(get_current_user)):
    """Get huntable creatures"""
    creatures = [c for c in MASTER_CREATURES if current_user['level'] >= c['min_level']]
    return creatures

@app.post("/api/game/hunting/hunt")
async def hunt_creature(req: HuntRequest, current_user: dict = Depends(get_current_user)):
    """Hunt creature"""
    user_id = current_user['id']
    
    creature = next((c for c in MASTER_CREATURES if c['id'] == req.creature_id), None)
    if not creature:
        raise HTTPException(status_code=404, detail="Kreatur nicht gefunden")
    
    if current_user['level'] < creature['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {creature['min_level']} erforderlich")
    
    current_energy = await regenerate_energy(current_user)
    if current_energy < creature['energy_cost']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Energie (benötigt: {creature['energy_cost']})")
    
    # Deduct energy
    await db.users.update_one(
        {'id': user_id},
        {'$inc': {'energy': -creature['energy_cost']}, '$set': {'last_energy_regen': datetime.now(timezone.utc)}}
    )
    
    # Combat calculation
    player_power = current_user['stats']['strength'] + current_user['stats']['dexterity'] + random.randint(0, 30)
    creature_power = creature['power'] + random.randint(0, 20)
    
    won = player_power > creature_power
    
    if won:
        gold_reward = random.randint(*creature['rewards']['gold'])
        xp_reward = creature['rewards']['xp']
        
        await db.users.update_one({'id': user_id}, {'$inc': {'gold': gold_reward, 'xp': xp_reward}})
        
        # Item chance
        item_gained = None
        if 'item_chance' in creature['rewards']:
            item_id, chance = creature['rewards']['item_chance']
            if random.randint(1, 100) <= chance:
                existing = await db.inventories.find_one({'user_id': user_id, 'item_id': item_id})
                if existing:
                    await db.inventories.update_one({'user_id': user_id, 'item_id': item_id}, {'$inc': {'quantity': 1}})
                else:
                    await db.inventories.insert_one({
                        'id': str(uuid.uuid4()),
                        'user_id': user_id,
                        'item_id': item_id,
                        'quantity': 1,
                        'acquired_at': datetime.now(timezone.utc)
                    })
                
                item_data = next((i for i in MASTER_ITEMS if i['id'] == item_id), None)
                item_gained = item_data['name'] if item_data else item_id
        
        await log_event('combat', f'{current_user["username"]} defeated a {creature["name"]}!', user_id)
        
        message = f'Sieg! +{gold_reward} Gold, +{xp_reward} XP'
        if item_gained:
            message += f', +1 {item_gained}'
        
        return {
            'success': True,
            'won': True,
            'message': message,
            'rewards': {'gold': gold_reward, 'xp': xp_reward, 'item': item_gained}
        }
    else:
        # Lost - take damage
        damage = random.randint(20, 40)
        current_hp = await regenerate_hp(current_user)
        new_hp = max(0, current_hp - damage)
        
        await db.users.update_one({'id': user_id}, {'$set': {'hp': new_hp, 'last_hp_regen': datetime.now(timezone.utc)}})
        
        # Hospital if needed
        if new_hp == 0:
            await db.hospital_sessions.insert_one({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'reason': 'hunting_injury',
                'admit_time': datetime.now(timezone.utc),
                'release_time': datetime.now(timezone.utc) + timedelta(minutes=45),
                'released': False
            })
        
        return {
            'success': True,
            'won': False,
            'message': f'Niederlage! -{damage} HP',
            'damage': damage,
            'hospitalized': new_hp == 0
        }

# ============================================================================
# BOUNTIES SYSTEM
# ============================================================================

@app.get("/api/game/bounties")
async def get_bounties(limit: int = 30):
    """Get active bounties"""
    bounties = await db.bounties.find({'active': True}, {'_id': 0}).sort('reward', -1).limit(limit).to_list(limit)
    return serialize_doc(bounties)

@app.post("/api/game/bounties/create")
async def create_bounty(req: BountyCreateRequest, current_user: dict = Depends(get_current_user)):
    """Place bounty on player"""
    user_id = current_user['id']
    
    # Find target
    target = await db.users.find_one({'username': req.target_username})
    if not target:
        raise HTTPException(status_code=404, detail="Ziel nicht gefunden")
    
    if target['id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst kein Kopfgeld auf dich selbst aussetzen")
    
    # Check if bounty already exists
    existing = await db.bounties.find_one({'target_id': target['id'], 'active': True})
    if existing:
        raise HTTPException(status_code=400, detail="Auf diesen Spieler ist bereits ein Kopfgeld ausgesetzt")
    
    # Check gold
    if current_user['gold'] < req.reward_amount:
        raise HTTPException(status_code=400, detail="Nicht genug Gold")
    
    # Deduct gold
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -req.reward_amount}})
    
    # Create bounty
    bounty = {
        'id': str(uuid.uuid4()),
        'target_id': target['id'],
        'target_name': target['username'],
        'target_level': target['level'],
        'placed_by_id': user_id,
        'placed_by_name': current_user['username'],
        'reward': req.reward_amount,
        'active': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.bounties.insert_one(bounty)
    
    await log_event('bounty', f'Kopfgeld auf {target["username"]}: {req.reward_amount} Gold!', user_id)
    
    return {
        'success': True,
        'message': f'Kopfgeld von {req.reward_amount} Gold auf {target["username"]} ausgesetzt'
    }

# ============================================================================
# PROPERTIES SYSTEM
# ============================================================================

@app.get("/api/game/properties/available")
async def get_available_properties(current_user: dict = Depends(get_current_user)):
    """Get properties available for purchase"""
    # Get owned properties
    owned = await db.user_properties.find({'user_id': current_user['id']}, {'property_id': 1}).to_list(100)
    owned_ids = [p['property_id'] for p in owned]
    
    # Filter available
    available = [p for p in MASTER_PROPERTIES if p['id'] not in owned_ids and current_user['level'] >= p['min_level']]
    
    return available

@app.post("/api/game/properties/buy")
async def buy_property(req: PropertyBuyRequest, current_user: dict = Depends(get_current_user)):
    """Buy property"""
    user_id = current_user['id']
    
    # Check if already owned
    existing = await db.user_properties.find_one({'user_id': user_id, 'property_id': req.property_id})
    if existing:
        raise HTTPException(status_code=400, detail="Du besitzt diese Immobilie bereits")
    
    # Find property
    prop = next((p for p in MASTER_PROPERTIES if p['id'] == req.property_id), None)
    if not prop:
        raise HTTPException(status_code=404, detail="Immobilie nicht gefunden")
    
    if current_user['level'] < prop['min_level']:
        raise HTTPException(status_code=400, detail=f"Level {prop['min_level']} erforderlich")
    
    if current_user['gold'] < prop['price']:
        raise HTTPException(status_code=400, detail=f"Nicht genug Gold (benötigt: {prop['price']})")
    
    # Purchase
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': -prop['price']}})
    
    await db.user_properties.insert_one({
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'property_id': req.property_id,
        'property_name': prop['name'],
        'purchased_at': datetime.now(timezone.utc),
        'last_collected': datetime.now(timezone.utc)
    })
    
    # Check achievement
    property_count = await db.user_properties.count_documents({'user_id': user_id})
    if property_count == 1:
        await check_and_award_achievement(user_id, 'property_owner')
    
    await log_event('market', f'{current_user["username"]} purchased property: {prop["name"]}', user_id)
    
    return {
        'success': True,
        'message': f'{prop["name"]} gekauft für {prop["price"]} Gold!'
    }

@app.get("/api/game/properties/my-properties")
async def get_my_properties(current_user: dict = Depends(get_current_user)):
    """Get owned properties"""
    properties = await db.user_properties.find({'user_id': current_user['id']}, {'_id': 0}).to_list(100)
    
    # Enrich with details
    enriched = []
    for prop in properties:
        prop_data = next((p for p in MASTER_PROPERTIES if p['id'] == prop['property_id']), None)
        if prop_data:
            # Calculate available income
            last_collected = prop.get('last_collected')
            if isinstance(last_collected, str):
                last_collected = datetime.fromisoformat(last_collected.replace('Z', '+00:00'))
            
            days_passed = (datetime.now(timezone.utc) - last_collected).total_seconds() / 86400
            available_income = int(days_passed * prop_data['daily_income'])
            
            enriched.append({
                **serialize_doc(prop),
                'property_details': prop_data,
                'available_income': available_income
            })
    
    return enriched

@app.post("/api/game/properties/collect/{property_id}")
async def collect_property_income(property_id: str, current_user: dict = Depends(get_current_user)):
    """Collect income from property"""
    user_id = current_user['id']
    
    user_prop = await db.user_properties.find_one({'id': property_id, 'user_id': user_id})
    if not user_prop:
        raise HTTPException(status_code=404, detail="Immobilie nicht gefunden")
    
    prop_data = next((p for p in MASTER_PROPERTIES if p['id'] == user_prop['property_id']), None)
    if not prop_data:
        raise HTTPException(status_code=404, detail="Immobilien-Daten nicht gefunden")
    
    last_collected = user_prop.get('last_collected')
    if isinstance(last_collected, str):
        last_collected = datetime.fromisoformat(last_collected.replace('Z', '+00:00'))
    
    days_passed = (datetime.now(timezone.utc) - last_collected).total_seconds() / 86400
    income = int(days_passed * prop_data['daily_income'])
    
    if income < 1:
        raise HTTPException(status_code=400, detail="Noch kein Einkommen verfügbar")
    
    # Collect
    await db.users.update_one({'id': user_id}, {'$inc': {'gold': income}})
    await db.user_properties.update_one(
        {'id': property_id},
        {'$set': {'last_collected': datetime.now(timezone.utc)}}
    )
    
    return {
        'success': True,
        'message': f'{income} Gold von {prop_data["name"]} eingesammelt',
        'income': income
    }

# ============================================================================
# MESSAGES SYSTEM
# ============================================================================

@app.get("/api/game/messages")
async def get_messages(current_user: dict = Depends(get_current_user), limit: int = 50):
    """Get inbox"""
    messages = await db.messages.find(
        {'recipient_id': current_user['id']},
        {'_id': 0}
    ).sort('sent_at', -1).limit(limit).to_list(limit)
    
    return serialize_doc(messages)

@app.post("/api/game/messages/send")
async def send_message(req: MessageSendRequest, current_user: dict = Depends(get_current_user)):
    """Send message"""
    user_id = current_user['id']
    
    # Find recipient
    recipient = await db.users.find_one({'username': req.recipient_username})
    if not recipient:
        raise HTTPException(status_code=404, detail="Empfänger nicht gefunden")
    
    if recipient['id'] == user_id:
        raise HTTPException(status_code=400, detail="Du kannst dir nicht selbst schreiben")
    
    # Create message
    message = {
        'id': str(uuid.uuid4()),
        'sender_id': user_id,
        'sender_name': current_user['username'],
        'recipient_id': recipient['id'],
        'recipient_name': recipient['username'],
        'subject': req.subject,
        'body': req.body,
        'read': False,
        'sent_at': datetime.now(timezone.utc)
    }
    await db.messages.insert_one(message)
    
    return {'success': True, 'message': f'Nachricht an {req.recipient_username} gesendet'}

@app.post("/api/game/messages/{message_id}/read")
async def mark_message_read(message_id: str, current_user: dict = Depends(get_current_user)):
    """Mark message as read"""
    message = await db.messages.find_one({'id': message_id, 'recipient_id': current_user['id']})
    if not message:
        raise HTTPException(status_code=404, detail="Nachricht nicht gefunden")
    
    await db.messages.update_one({'id': message_id}, {'$set': {'read': True}})
    
    return {'success': True}

# ============================================================================
# HOSPITAL & DUNGEON STATUS
# ============================================================================

@app.get("/api/game/hospital")
async def get_hospital_patients(limit: int = 30):
    """Get hospitalized players"""
    sessions = await db.hospital_sessions.find(
        {'released': False},
        {'_id': 0}
    ).sort('admit_time', -1).limit(limit).to_list(limit)
    
    return serialize_doc(sessions)

@app.get("/api/game/dungeon")
async def get_dungeon_inmates(limit: int = 30):
    """Get jailed players"""
    sessions = await db.dungeon_sessions.find(
        {'released': False},
        {'_id': 0}
    ).sort('arrest_time', -1).limit(limit).to_list(limit)
    
    return serialize_doc(sessions)

# ============================================================================
# ACHIEVEMENTS
# ============================================================================

@app.get("/api/game/achievements")
async def get_achievements(current_user: dict = Depends(get_current_user)):
    """Get achievements"""
    # Get earned
    earned = await db.user_achievements.find({'user_id': current_user['id']}, {'achievement_id': 1}).to_list(100)
    earned_ids = [a['achievement_id'] for a in earned]
    
    # All achievements
    all_achievements = []
    for ach in MASTER_ACHIEVEMENTS:
        all_achievements.append({
            **ach,
            'earned': ach['id'] in earned_ids
        })
    
    return all_achievements

# ============================================================================
# LANDING PAGE ENDPOINTS (PRESERVE EXISTING)
# ============================================================================

async def get_real_leaderboard(limit: int = 10) -> list:
    """Get real leaderboard from users"""
    users = await db.users.find(
        {},
        {"_id": 0, "password": 0, "email": 0}
    ).sort([("level", -1), ("xp", -1)]).limit(limit).to_list(limit)
    
    result = []
    for rank, u in enumerate(users, start=1):
        created = u.get("created_at")
        if isinstance(created, datetime):
            created_dt = created
        else:
            created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        
        days_in_realm = (datetime.now(timezone.utc) - created_dt).days
        
        path_key = u.get("path_choice", "knight")
        result.append({
            "rank": rank,
            "username": u.get("username", "Unknown"),
            "title": u.get("title", "Adventurer"),
            "age": days_in_realm,
            "level": u.get("level", 1),
            "xp": u.get("xp", 0),
            "path_choice": path_key,
            "path_label": PATH_LABELS.get(path_key, "Knight"),
            "path_icon": PATH_ICONS.get(path_key, "⚔️"),
            "improvement": round(u.get("xp", 0) / max(days_in_realm, 1), 2) if days_in_realm > 0 else 0.0,
        })
    return result

async def get_real_online_stats() -> dict:
    """Get real online stats"""
    now = datetime.now(timezone.utc)
    time_15m = now - timedelta(minutes=15)
    time_1h = now - timedelta(hours=1)
    time_24h = now - timedelta(hours=24)
    
    now_count = await db.users.count_documents({"last_seen": {"$gte": time_15m}})
    hour_count = await db.users.count_documents({"last_seen": {"$gte": time_1h}})
    day_count = await db.users.count_documents({"last_seen": {"$gte": time_24h}})
    total_count = await db.users.count_documents({})
    
    return {
        "now": now_count,
        "last_hour": hour_count,
        "last_24h": day_count,
        "total": total_count,
    }

async def get_real_ticker() -> list:
    """Get real event ticker"""
    events = await db.events.find({}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    return serialize_doc(events)

@app.get("/api/landing")
async def get_landing():
    """Landing page data"""
    leaderboard = await get_real_leaderboard(10)
    ticker = await get_real_ticker()
    online = await get_real_online_stats()
    features = await db.features.find({}, {"_id": 0}).sort("index", 1).to_list(100)
    reviews = await db.reviews.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    
    # Format reviews
    enriched_reviews = []
    for review in reviews:
        created = review.get('created_at')
        if isinstance(created, datetime):
            created_dt = created
        else:
            created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        
        days_ago = (datetime.now(timezone.utc) - created_dt).days
        if days_ago == 0:
            date_str = "Heute"
        elif days_ago == 1:
            date_str = "Gestern"
        elif days_ago < 30:
            date_str = f"vor {days_ago} Tagen"
        else:
            date_str = created_dt.strftime("%-d. %B %Y")
        
        enriched_reviews.append({
            'id': review['id'],
            'author': review['author'],
            'rating': review['rating'],
            'text': review['text'],
            'verified': True,
            'date': date_str
        })
    
    news = await db.news.find({}, {"_id": 0}).to_list(100)
    paths = await db.paths.find({}, {"_id": 0}).to_list(10)
    kingdoms = await db.kingdoms.find({}, {"_id": 0}).to_list(20)
    
    return {
        "ticker": ticker,
        "leaderboard": leaderboard,
        "online": online,
        "features": serialize_doc(features),
        "reviews": enriched_reviews,
        "news": serialize_doc(news),
        "paths": serialize_doc(paths),
        "kingdoms": serialize_doc(kingdoms),
    }

@app.get("/api/reviews")
async def get_reviews_only():
    """Just reviews for landing"""
    reviews = await db.reviews.find({}, {'_id': 0}).sort('created_at', -1).to_list(100)
    
    enriched = []
    for review in reviews:
        created = review.get('created_at')
        if isinstance(created, datetime):
            created_dt = created
        else:
            created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
        
        days_ago = (datetime.now(timezone.utc) - created_dt).days
        if days_ago == 0:
            date_str = "Heute"
        elif days_ago == 1:
            date_str = "Gestern"
        elif days_ago < 30:
            date_str = f"vor {days_ago} Tagen"
        else:
            date_str = created_dt.strftime("%-d. %B %Y")
        
        enriched.append({
            'id': review['id'],
            'author': review['author'],
            'rating': review['rating'],
            'text': review['text'],
            'verified': True,
            'date': date_str
        })
    
    return enriched

@app.post("/api/reviews")
async def create_review(req: ReviewRequest, current_user: dict = Depends(get_current_user)):
    """Create review"""
    existing = await db.reviews.find_one({'user_id': current_user['id']})
    if existing:
        raise HTTPException(status_code=400, detail="Du hast bereits eine Bewertung abgegeben")
    
    review = {
        'id': str(uuid.uuid4()),
        'user_id': current_user['id'],
        'author': current_user['username'],
        'rating': req.rating,
        'text': req.text,
        'verified': True,
        'created_at': datetime.now(timezone.utc)
    }
    await db.reviews.insert_one(review)
    
    return {'success': True, 'message': 'Vielen Dank für deine Bewertung!'}

# ============================================================================
# CORS SETUP
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
