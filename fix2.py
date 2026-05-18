with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('var history = []', 'var chatHistory = []')
content = content.replace('history.push', 'chatHistory.push')
content = content.replace('messages: history', 'messages: chatHistory')
content = content.replace('{ role: "user", content: text || "Analyse cette image" }', '{ role: "user", content: text || "Analyse cette image" }')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("OK!")