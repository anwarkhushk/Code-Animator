import ollama

try:
    print("Listing models...")
    response = ollama.list()
    # response is usually {'models': [...]} object or list of objects
    # Let's verify type
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    
    models = response.get('models', [])
    print(f"Found {len(models)} models.")
    for m in models:
        # m might be a dict or object
        name = m.get('name') if isinstance(m, dict) else getattr(m, 'name', str(m))
        print(f" - {name}")

except Exception as e:
    print(f"Error: {e}")
