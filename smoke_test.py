from app import create_app
app = create_app()
client = app.test_client()
res = client.get('/api/system/status')
print('status', res.status_code)
print(res.get_json())
