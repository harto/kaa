def add(a, b):
    return a + b

# todo: build dynamically? using e.g. decorators
def env():
    return {'+': add}
