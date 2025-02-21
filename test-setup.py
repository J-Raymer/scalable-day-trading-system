import requests
from faker import Faker

fake = Faker()
fake.seed_instance(12345)

def register():
    data = {
        "user_name": "test",
        "name": "test",
        "password": "password"
    }
    response = requests.post("http://localhost:3001/authentication/register", json=data, verify=False)
    return response.json()

def setup_stocks(token: str):
    stock_data = {
        "stock_name": fake.company(),
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post("http://localhost:3001/setup/createStock", json=stock_data, headers=headers)
    stock = response.json()
    return stock

def add_single_stock_to_user(token: str, stock_id: str):
    stock_data = {
        "stock_id": stock_id,
        "quantity":100
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.post("http://localhost:3001/setup/addStockToUser", json=stock_data, headers=headers)
    return response.json()

def main():

    try:
        res = register()
        token = res['data']['token']
        results = list(map(lambda _: setup_stocks(token), range(20)))
        added_stocks = list(map(lambda stock: add_single_stock_to_user(token, stock['data']['stock_id']), results[0:5]))
        print('Set up user data and stocks')
        print('User data', res['data'])
        print('added stocks to user', added_stocks)
        print('Stocks', results)
    except Exception as e:
        print('Exception occurred setting up tests', e)


if __name__ == "__main__":
    main()
