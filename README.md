# ʵ�鱨��
���������  
ѧ�ţ�10225501448
## 1. ��������
��pj1�Ŀ��������У�������һ���汾����sqlite���ݿ���ʵ���˴󲿷ֹ��ܡ��������ʹ���˰汾�����ҵ��˸ð汾���ڴ˻����ϲ�ȫ���¿����Ĺ��ܣ��������ݿ���ƣ�ת�����ݿ���postgresql�����н�һ���Ŀ�����  

## 2. ���ݿ����
### 2.1 ERͼ
![alt text](pics/4.png)
### 2.2 ������Ϣ�����˼·
���ʹ�������ĵ����ݿ⣬��ϵ���ݿⱻ���Ƴ�һ������ϵ��ɵı�񣬲�ʧȥ��Ƕ�׵����������ڴ�ͬʱ�������������ǣ������֮��Ĺ�ϵ����������
```user_```
| ���� | ���� | �� |
| ---  | --- | ---|
|user_id|text|����
|password|text
|balance|int
|token|text
|terminal|text
|bids|text

```user_store```
| ���� | ���� | �� |
| ---  | --- | ---|
|user_id|text|���: user(user_id)
|store_id|text|����

```store```
| ���� | ���� | �� |
| ---  | --- | ---|
|store_id|text|�����user_store(store_id), ��book_id��������
|book_id|text|��store_id��������
|book_info|text
|stock_level|text  

����user��store��Ĺ�ϵ�����ĵ����ݿ������ڿ��԰�store��������ϳ�һ���б����һ���ĵ��У�store_id������Ϊstore����������ʹ�������ĵ�ʵ����һһ��Ӧ��������Ҫ�����user_store�����ǽ�user��Ϊstore��һ���ֶΡ����ڹ�ϵ���ݿ��У�һ������ϵ�����ƾ�����store��book_idֻ����Ϊ����������user��store�䱣��һ�Զ��ϵ������ʹ��user_store���������Ӳ�ѯ���Եñ�Ҫ���������ˡ�

�ܽ�һ������Ĺ�ϵ���û�ע��ʱ����Ϣ���뵽user����ע����û���user_id������ƣ����̵�ʱ���̵�id����user_store���ѵǼǵ��̵꣨store_id������ƣ�����ʱ����Ϣ����store���С�  

user_���¼���bids�ֶ��ڲ�ѯʱʹ�á������ɿɼ�pj1 4.3���֣�  

```new_order```
| ���� | ���� | �� |
| ---  | --- | ---|
|order_id|text|����
|user_id|text|���: user(user_id)
|store_id|text|�����user_store(store_id)
|state|text
|order_datetime|text

```new_order_detail```
| ���� | ���� | �� |
| ---  | --- | ---|
|order_id|text|���: new_order(order_id), ��book_id��������
|book_id|text|��order_id��������
|count|int
|price|int

```history_order```
| ���� | ���� | �� |
| ---  | --- | ---|
|order_id|text|����
|user_id|text|���: user(user_id)
|store_id|text|�����user_store(store_id)
|state|text
|order_datetime|text

```history_order_detail```
| ���� | ���� | �� |
| ---  | --- | ---|
|order_id|text|���: history_order(order_id), ��book_id��������
|book_id|text|��order_id��������
|count|int
|price|int

�������Ŷ��������ƺ��ĵ����ݿ��в�𲻴�ֻ�Ǽ���order_id���������ǿ��������ϵ��ԭ����Ҫ���������ݷ��룬���컯��������ǿ���ܡ�����pj1�ı���������ϸ˵����4.2���֣������ﲻ��׸����

```book```**(nosql)**
```
book{
    id
    title
    author
    ...
    content
    tags
    pictures
}
```

��Ȼʵ��Ҫ����˵���Խ�blob���ݷ���洢������ʵ��ʵ����������ѡ�������鱾��Ϣ�Ծɴ洢��mongodb�С�����Ҫ�ǳ������¿�����  
1. �����С���Դ�sql�������Դ�nosql����ô���Ҫ�õ�һ�����������Ϣ��Ҫ��ѯ�������ݿ⣬���Ӳ���Ҫ�Ŀ�����
2. �����С���Դ�sql�������������һ����nosql�����ݲ�ͬ�����ѯ��ͬ�����ݿ⣬��ôsql�е�����ʵ�ʶ������࣬����Ҳֱ��ͨ��nosql��ѯС���ԡ�
3. �鱾����Ϣһ���洢�����������޸ģ���������Ϊ����ѯ��Ϣ����˹�ϵ���ݿ��һ�����ơ�������֧��Ҳ�ò�̫����
���ϣ���ѡ����Ȼʹ��nosql�洢�鱾��Ϣ��book_id��Ϊ����ʹ�õ�Լ���������ʵ�ֹ�������ͬ�����鱾��Ϣ�洢��sql�н��г��ԱȽϣ��洢�����ļ�Ϊbookstore/fe/data/save_psql.py��  

## 3. �¹���ʵ��
### 3.1 �ջ�������ȡ������
ͨ��������state�ֶΣ����Ա���һ���������µ������͵��������л�����Ϊ������ʱ��ȡ����״̬�����µ���ɺ󣬶���״̬��Ϊ `wait for payment`����������Ϻ󣬶���״̬��Ϊ `wait for delivery`�������ҷ����󣬶���״̬��Ϊ `delivering`��������ջ��󣬶���״̬��Ϊ `received`�����û��ڸ����ʱ�򽫵�ǰʱ����µ�ʱ����бȽϣ�`order_datetime`�ֶΣ����ڳ���һ��ʱ��δ�����ʱ��ȡ������������״̬��Ϊ `cancelled`�����û�����ȡ��������ʱ�򣬶���״̬Ҳ��Ϊ `cancelled `��ÿһ��״̬�ı仯�ϲ���һ��������ύ��������ֹ�˶���״̬���쳣����ַ����������ACID�ĸ����ԡ�  
�������϶࣬�����չʾ�ջ�������Ϊ���ӣ�  
```python
    def receive(self, user_id: str, order_id: str) -> tuple[(int,str)]:
        conn = self.conn
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            conn.execute(
                "UPDATE history_order SET state='received' "
                "WHERE user_id=%s AND order_id=%s AND state='delivering'",
                (user_id,order_id)
            )

            self.con.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok"
```

### 3.2 ��ʷ������ѯ
�ڲ�ѯ��ʷ������ʱ������ʹ�ö�����ӵķ�ʽ���в�ѯ��MongoDB��ʵ�ֶ�����ӣ�`lookup`��ʱ���Ὣ�±��ĵ��ϲ���һ�����飬�Ҷ������ɸѡ�����ùܵ�������ʮ�ָ��ӣ��������ϵĲ�ѯ��ʽ��sql�����ȼۡ���pj1��ʵ����Ҳ����ʵ����sql�汾�ٽ����滻��������Ҳ���ѷ��֣���ҵ���漰������ϵʱ���ĵ����ݿ���ʽ�����ŵ���ʵ���Ѷ��Ϸ����������ƣ�����ϵ���ݿ���ʽ����һ��ʼ���ܹ�ϵ���ƣ�ȴ�ڴ�ʱ���ø�����sql����ʵ�ֲ�ѯ��  
�����ٴ�չʾ�����汾�Ĵ��빩�Ƚ���ͬ��  
```python           
            # match1 = {'$match': {'user_id': user_id}}
            # look_up1 = {'$lookup': {'from': 'his_order_detail', 
            #                        'localField': 'order_id', 
            #                        'foreignField': 'order_id', 
            #                        'as': 'order_detail'}} 
            # look_up2 = {'$lookup':{'from': 'store',
            #                        'localField': 'store_id',
            #                        'foreignField': 'store_id',
            #                        'as': 'store_item'}}
            # project = {'$project': {'_id': 0, 'order_id': 1, 'store_id': 1, 'state': 1, 'order_datetime': 1,
            #                         'book_id': '$order_detail.book_id', 'count': '$order_detail.count', 'price': '$order_detail.price',
            #                         'difference': {'$in': ['$order_detail.book_id', '$store_item.books.book_id']}}}
            # match2 = {'$match': {'difference': True}}
            # rows = col_his_order.aggregate([match1, look_up1, look_up2, project, match2])          
            sql="""
                select A.order_id,A.store_id,state,order_datetime,B.book_id,count,price 
                from history_order as A 
                join history_order_detail as B on A.order_id=B.order_id
                join store as C on A.store_id=C.store_id and B.book_id=C.book_id
                where user_id='{}'""".format(user_id)
            conn.execute(sql)
            res = conn.fetchall()     
            self.con.commit()
```

### 3.3 ����ͼ��
��������ͼ�飬�Ҳ����˷�ҳ��ƣ�ͬʱ�������ܺ�ҵ������Ŀ����������pj1 4.3���֣��������������ѯ�Ĳ�ѯ�߼���������������ص�sql��nosql��ϵ����ݿ���ƣ��ھ���ʵ��ʱҲ�������������ϣ���Ҫ�鱾������Ϣ����ģ����ѯʱ����nosql���õ���ѯ���book_idʱ����user_���Ա������ҳ�������������ϸ�ڴ����ǣ���ԭ��������ʽ��book_id�ö��ŷָ��ϳ��ַ������Ա�����ϵ���ݿ⡣��  
����ʵ�����£�  
```python
    def search(self,user_id:str,keyword:str,content:str,store_id:str) -> tuple[(int,str,int)]:
        conn = self.conn
        try:
            self.conn.execute(
                "UPDATE user_ SET bids = %s WHERE user_id = %s",
                ('', user_id),
            )
            self.con.commit()
            
            keys = self.col_book.find_one().keys()
            if keyword not in keys or keyword == '_id':
                return error.error_wrong_keyword(keyword)+(-1,)
            
            sql = """select distinct book_id from store """
            if not store_id == "":
                sql += " where store_id='{}'".format(store_id)
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)+(-1,)
            conn.execute(sql)
            row = conn.fetchall()
            if row == []:
                return 200,"ok",0
            bids = list(map(lambda x:x[0],row))
            # bids:tuple[str,]=tuple(map(lambda x:x[0],row))
            # if len(bids) == 1 :
            #     bids="('"+str(bids[0])+"')"
            rows = self.col_book.find({'id': {'$in': bids}, keyword: {'$regex':  content}}, 
                               {'_id': 0, 'id': 1})
            res = list(map(lambda x:x['id'],rows)) 
            # search_sql="""select id from {} 
            #     where id in {} and {} like '%{}%'""".format(book_tb,bids,keyword,content)
            # conn.execute(search_sql)
            # row = conn.fetchall()
            # if row == []:
            #     return 200,"ok",0
            # res = list(map(lambda x:x[0],row))
            bids = ','.join(res)
            conn.execute(
                "UPDATE user_ SET bids = %s WHERE user_id = %s",
                (bids, user_id),
            )
            self.con.commit()
            pages = len(res) // SEARCH_PAGE_LENGTH #�������ҳ
        except psycopg2.Error as e:
            logging.error(e)
            return 528, "{}".format(str(e)),-1
        except mongo_error.PyMongoError as e:
            logging.error(e)
            return 529, "{}".format(str(e)),-1
        except BaseException as e:
            logging.error(e)
            return 530, "{}".format(str(e)),-1
        return 200,"ok",pages
```
������ҳ�Ľӿڲ��漰���ݿ������������pj1���֣�����Ҳ����չʾ����Ҳ�����˴���ӿھ������õĸ����ԡ�

## 4. ���Խ��
### 4.1 �����ʲ���
�����������渴����pj1ʱ��д����������������΢���䣬��������pj1�ı�����û�н��г�ֽ��ܣ�������¼ӵ������ӿڽ��в�����ܡ�  
**test_cancel_order**
test_ok: ��������ȡ������  
test_non_exist_order_id������ȡ�������Ų����ڵĶ��� 
test_non_exit_user_id������ȡ���µ��˲����ڵĶ���  

**test_deliver**
test_ok: ������������  
test_non_exist_order_id�����Է��������Ų����ڵĶ���  
test_non_exit_user_id�����Է����µ��˲����ڵĶ���  

**test_payment**
test_ok: ����������ֵ��֧��  
test_authorization_error��������������µĵ�¼֧��ʧ��  
test_not_suff_funds�����Դ��㵼�µ�֧��ʧ��  
test_repeat_pay�������ظ��µ�
test_time_out�����Զ�����ʱ

**test_receive**
test_ok: ���Գ�ֵ��֧���������ջ�����
test_non_exist_order_id�������յ������Ų����ڵĶ���  
test_non_exit_user_id�������յ��µ��˲����ڵĶ���  

**test_history_order**
test_ok: ����������ѯ���û����е���ʷ����
test_non_exit_user_id�����Բ�ѯ�����ڵ��û�����ʷ����  

**test_search**
test_ok: �����������ݱ����ѯ�������õ���ȷ��id  
test_not_in: ���Բ�ѯ���������ڵ��飬�������ص��޽��id  
test_next_and_pre_and_specific: ����һ��������ѯ���౾�飬����ǰ�����ض���ҳ  
test_non_next_and_pre_and_specific������ǰ�����ض����������ڵ�ҳ������ʧ��  
test_partial_name: ���Խ�ȡ������������ģ����ѯ  
test_wrong_keyword: ���Ը��ݲ����ڵ��ֶν��в�ѯ������ʧ��
test_specific_store: ���϶���ȫ�̵�������������Խ������һ�ҵ꣬������һ�ҵ��������飬�õ������ڵĽ��
test_wrong_store_id: �����ڲ����ڵ��̵�����
test_zero_stock: ������û������̵��������������ص��޽��id  

���Խ�����£�  
![alt text](pics/1.png)
![alt text](pics/2.png)
���ǵ�ÿ�����������������е��Դ��룬�������������ܸ������з�֧��  
![alt text](pics/3.png)

### 4.2 ���ܲ���
����ͬ��������pj1�е��ԸĽ��Ĵ��루����˼ٲ��������������������������޵�bug��  
���Ի���: Intel(R) Core(TM) i9-14900HX 24��32�߳� 16GB�ڴ�
�������: 
�����ʣ� 
![alt text](pics/6.png)
�µ��ӳ٣�
![alt text](pics/5.png)

�ڿ�ʼʱ��߲���������õ������ʵ����������ǵ�һ���̶ȸ��ر��ͣ������������ȶ���������ζ���������µ��ӳٵĽ�������Կ����ӳ����Ų����߳������Ӳ������ӣ�����Ԥ�ڡ�

## 5. �����ܽ�
1. ���ʵ�ֵĴ���û�в�׽�����ִ��󣬵��µ���ʱ��׽����һ����������жϣ������ж�ǰһ�εĴ��󾿾������ֻ��������С��Χ�Ų�ķ���ȷ�����⣬Ӱ����Ч�ʡ�  
2. �������ʱ��û��ע�⵽������ݵ�ɾ�������������˳�򣬼���һ��ԭ���������ã�����ֱ����psql�ն˲鿴��ʱ�ŷ������⡣

## 6. �汾����
������Ҫ������pj1�İ汾���˺ͽ�һ��������������ε���Ŀ�ǵ��˵ģ��׶�ʵ�ֵĴ���򵥴�����˱����ݴ�����ȫ����ɺ�һ�����͵��˲ֿ⡣�ֿ��ַ�� https://github.com/augurier/book_store ��