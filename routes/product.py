from app import app, connection, text, request


@app.route('/get_all_product')
def getAllProduct():
    category = connection.execute(text("""SELECT * FROM category """))

    result = connection.execute(text(
        """
        SELECT 
            product.*,
            category.name as 'category'
        FROM product 
        join category on product.category_id = category.id
        """
    ))
    connection.commit()
    product_arr = []
    for item in result:
        product_arr.append(
            {
                'id': item.id,
                'name': item.name,
                'category_id': item.category_id,
                'image': item.image,
                'cost': item.cost,
                'price': item.price,
                'category': item.category,
            }
        )

    category_arr = []
    for item_cat in category:
        category_arr.append(
            {
                'id': item_cat.id,
                'name': item_cat.name,
            }
        )
    data = {
        'product': product_arr,
        'category': category_arr
    }
    return data


@app.route('/get_product_by_filter')
def getProductByFilter():
    txt_src = request.args.get('txt_src')
    result = connection.execute(text(f"SELECT * FROM product where name like '%{txt_src}%'"))
    product_arr = []
    for item in result:
        product_arr.append(
            {
                'id': item.id,
                'name': item.name,
                'category_id': item.category_id,
                'image': item.image,
                'cost': item.cost,
                'price': item.price,
            }
        )

    return product_arr


@app.route('/get_product_by_category', methods=['POST'])
def getProductByCategory():
    if request.method == "POST":
        category_id = request.json['category_id']
        if category_id == 'all':
            result = connection.execute(text(
                f"""
                SELECT 
                    product.*,
                    category.name as 'category'
                FROM product 
                join category on product.category_id = category.id
                """
            ))
            connection.commit()
        else:
            # result = connection.execute(text(f"SELECT * FROM product where category_id = '{category_id}'"))
            result = connection.execute(text(
                f"""
                SELECT 
                    product.*,
                    category.name as 'category'
                FROM product 
                join category on product.category_id = category.id
                where product.category_id = '{category_id}'
                """
            ))
            connection.commit()

        product_arr = []
        for item in result:
            product_arr.append(
                {
                    'id': item.id,
                    'name': item.name,
                    'category_id': item.category_id,
                    'category': item.category,
                    'image': item.image,
                    'cost': item.cost,
                    'price': item.price,
                }
            )
        return product_arr