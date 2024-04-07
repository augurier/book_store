def set_order_state(col_order, order_id, new_state, old_state = 'any'): 
    target = {'order_id': order_id}
    if old_state != 'any':
        target['state'] = old_state   
              
    rows = col_order.update_one(target, {'$set': {'state': new_state}})
    
    if rows.matched_count != 1:
        return False
    else:
        return True
    
#order or detail
def new_to_his(col_new, col_his, order_id):
    rows = col_new.find({'order_id': order_id}, {'_id': 0})
    for row in rows:
        col_his.insert_one(row)
    rows = col_new.delete_many({'order_id': order_id})
        
    if rows.deleted_count == 0:
        return False
    else:
        return True