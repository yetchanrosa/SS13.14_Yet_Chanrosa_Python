import json
from urllib.parse import urlencode
from datetime import date
from app import app, connection, text, request, render_template


@app.route('/pos')
def indexPos():
    return render_template('pos.html')

@app.route('/pos/create', methods=['post'])
def createPos():
    try:
        received_amount = request.form.get('received_amount')
        selected_item = request.form.get('selected_item')
        selected_item_obj = json.loads(selected_item)

        # Insert sale transaction
        result = connection.execute(text(f"INSERT INTO sale (date, customer_id, received_amount) VALUES ('2023-12-26', 1, {received_amount})"))
        sale_id = result.lastrowid

        # Insert sale_detail data
        for item in selected_item_obj:
            pro_id = item['id']
            qty = item['qty']
            cost = item['cost']
            price = item['price']

            connection.execute(text(f"""
                INSERT INTO sale_detail (sale_id, product_id, qty, cost, price) 
                VALUES ({sale_id}, {pro_id}, {qty}, {cost}, {price})
            """))
            connection.commit()

        # Retrieve data for constructing the message
        current_sale = connection.execute(text(f"SELECT * FROM sale WHERE id = {sale_id}"))
        current_sale_detail = connection.execute(text(f"""
            SELECT sale_detail.*, product.name 
            FROM sale_detail 
            JOIN product ON sale_detail.product_id = product.id 
            WHERE sale_id = {sale_id}
        """))

        last_sale = []
        last_sale_detail_obj = []

        for sale_detail in current_sale_detail:
            last_sale_detail_obj.append({
                'id': sale_detail.id,
                'product_id': sale_detail.product_id,
                'product_name': sale_detail.name,
                'qty': sale_detail.qty,
                'cost': sale_detail.cost,
                'price': sale_detail.price,
            })

        for sale in current_sale:
            last_sale.append({
                'id': sale.id,
                'date': sale.date,
                'customer_id': sale.customer_id,
                'received_amount': sale.received_amount,
                'sale_detail': last_sale_detail_obj
            })

        # Construct the message
        message = (
            "<strong>សរុប:$ {grand_total}</strong>\n"
            "<code>បានទទួលប្រាក់: ${received_amount}</code>\n"
            "<code>ប្រាក់ត្រឡប់: ${cash_return}</code>\n"
            "<code>📆 {date}</code>\n"
            "<code>=======================</code>\n"
            
        ).format(
            grand_total=sum(item['qty'] * item['price'] for item in last_sale_detail_obj),
            received_amount=last_sale[0]['received_amount'],
            cash_return=last_sale[0]['received_amount']-sum(item['qty'] * item['price'] for item in last_sale_detail_obj),
            date=date.today()
        )

        for index, item in enumerate(last_sale_detail_obj, start=1):
            message += "<code>{index}. {name} {qty}x{price}</code>\n".format(
                index=index,
                name=item['product_name'],
                qty=item['qty'],
                price=item['price']
            )

        message = requests.utils.quote(message)

        # Send notification to the Telegram channel
        bot_token = "6325946724:AAEeg6BTeH9D7sigJxNTy92ydeor6ErI4cg"
        chat_id = "@net09871"
        config_url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}&parse_mode=HTML"
        res = requests.get(config_url)

        return last_sale

    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
        return {'error': f"{e}"}, 201