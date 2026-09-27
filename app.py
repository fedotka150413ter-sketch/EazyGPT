import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Получаем API-ключ из переменных окружения Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Полный HTML + Tailwind CSS код приложения
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EazyGPT — AI Assistant</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Highlight.js для подсветки кода -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <!-- Marked.js для рендеринга Markdown -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.js"></script>
    <style>
        .message-content pre { background-color: #1e1b4b; padding: 1rem; border-radius: 0.5rem; margin-top: 0.5rem; overflow-x: auto; }
        .message-content code { font-family: monospace; }
        .message-content p { margin-bottom: 0.75rem; }
        .message-content ul { list-style-type: disc; padding-left: 1.5rem; margin-bottom: 0.75rem; }
    </style>
</head>
<body class="bg-slate-900 text-slate-100 flex h-screen overflow-hidden">

    <!-- Боковая панель (история чатов) -->
    <div id="sidebar" class="bg-slate-950 w-64 flex flex-col justify-between border-r border-slate-800 transition-all duration-300 -translate-x-full md:translate-x-0 absolute md:relative z-20 h-full">
        <div class="p-4 flex flex-col h-full">
            <button onclick="newChat()" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 transition shadow-lg shadow-indigo-600/20 mb-6">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                Новый чат
            </button>
            <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">История</div>
            <div id="chat-history-list" class="flex-1 overflow-y-auto space-y-1 pr-1">
                <!-- История чатов динамически -->
            </div>
        </div>
        <div class="p-4 border-t border-slate-800 text-xs text-slate-500 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Облачный сервер активен
        </div>
    </div>

    <!-- Основная область чата -->
    <div class="flex-1 flex flex-col h-full bg-slate-900 relative">
        <!-- Шапка -->
        <header class="h-14 border-b border-slate-800 flex items-center justify-between px-4 bg-slate-900/80 backdrop-blur z-10">
            <div class="flex items-center gap-3">
                <button onclick="toggleSidebar()" class="md:hidden text-slate-400 hover:text-white">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </button>
                <h1 class="font-semibold text-lg bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">EazyGPT</h1>
            </div>
        </header>

        <!-- Контейнер сообщений -->
        <div id="chat-container" class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
            <div class="flex gap-4 max-w-3xl mx-auto items-start">
                <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0 font-bold text-sm shadow-md">AI</div>
                <div class="bg-slate-800/80 border border-slate-700/50 rounded-2xl p-4 shadow-sm message-content flex-1">
                    Привет! Я твой персональный ИИ-ассистент. Ты можешь писать мне вопросы, а также прикреплять фото из галереи или текстовые файлы через кнопку со скрепкой. Чем могу помочь?
                </div>
            </div>
        </div>

        <!-- Поле ввода сообщения и файлов -->
        <div class="p-4 bg-slate-900 border-t border-slate-800">
            <div class="max-w-3xl mx-auto">
                <!-- Плашка прикрепленного файла -->
                <div id="file-indicator" class="hidden items-center justify-between bg-slate-800 border border-indigo-500/30 rounded-xl px-3 py-1.5 mb-2 text-xs text-indigo-300">
                    <div class="flex items-center gap-2 truncate">
                        <svg class="w-4 h-4 shrink-0 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                        <span id="file-name" class="truncate font-medium"></span>
                    </div>
                    <button onclick="removeFile()" class="text-slate-400 hover:text-red-400 font-bold px-1.5">✕</button>
                </div>

                <form id="chat-form" onsubmit="sendMessage(event)" class="relative flex items-center">
                    <!-- Атрибут accept открывает галерею на телефонах или выбор документов -->
                    <input type="file" id="file-input" accept="image/*,.txt,.py,.json,.csv,.log" class="hidden" onchange="handleFileSelect(event)">
                    <button type="button" onclick="document.getElementById('file-input').click()" class="absolute left-3 text-slate-400 hover:text-indigo-400 transition p-2" title="Выбрать фото из галереи или файл">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                    </button>

                    <textarea id="user-input" rows="1" placeholder="Введите сообщение или прикрепите фото/файл..." class="w-full bg-slate-800 border border-slate-700 rounded-2xl pl-12 pr-14 py-3.5 focus:outline-none focus:border-indigo-500 resize-none text-slate-100 placeholder-slate-400 shadow-inner" onkeydown="handleKeyDown(event)"></textarea>
                    
                    <button type="submit" id="send-btn" class="absolute right-2 bg-indigo-600 hover:bg-indigo-500 text-white p-2.5 rounded-xl transition shadow-md">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"></path></svg>
                    </button>
                </form>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('-translate-x-full');
        }

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                selectedFile = file;
                document.getElementById('file-name').textContent = file.name;
                document.getElementById('file-indicator').classList.remove('hidden');
                document.getElementById('file-indicator').classList.add('flex');
            }
        }

        function removeFile() {
            selectedFile = null;
            document.getElementById('file-input').value = '';
            document.getElementById('file-indicator').classList.remove('flex');
            document.getElementById('file-indicator').classList.add('hidden');
        }

        function handleKeyDown(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage(event);
            }
        }

        async function sendMessage(event) {
            event.preventDefault();
            const input = document.getElementById('user-input');
            const messageText = input.value.trim();
            if (!messageText && !selectedFile) return;

            const chatContainer = document.getElementById('chat-container');

            let displayHtml = messageText;
            if (selectedFile) {
                displayHtml += `<br><span class="inline-flex items-center gap-1 mt-2 text-xs bg-indigo-950/80 text-indigo-300 px-2 py-1 rounded border border-indigo-500/20">📎 Прикреплен файл: ${selectedFile.name}</span>`;
            }

            const userMsgDiv = document.createElement('div');
            userMsgDiv.className = 'flex gap-4 max-w-3xl mx-auto items-start justify-end';
            userMsgDiv.innerHTML = `
                <div class="bg-indigo-600 text-white rounded-2xl p-4 shadow-sm message-content max-w-xl">${displayHtml}</div>
                <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0 font-bold text-sm shadow-md">Вы</div>
            `;
            chatContainer.appendChild(userMsgDiv);

            let fileContent = "";
            let fileName = "";
            if (selectedFile) {
                fileName = selectedFile.name;
                fileContent = await selectedFile.text();
            }

            input.value = '';
            removeFile();
            chatContainer.scrollTop = chatContainer.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            const aiMsgDiv = document.createElement('div');
            aiMsgDiv.id = loadingId;
            aiMsgDiv.className = 'flex gap-4 max-w-3xl mx-auto items-start';
            aiMsgDiv.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0 font-bold text-sm shadow-md">AI</div>
                <div class="bg-slate-800/80 border border-slate-700/50 rounded-2xl p-4 shadow-sm text-slate-400 animate-pulse">Думает...</div>
            `;
            chatContainer.appendChild(aiMsgDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: messageText, file_name: fileName, file_content: fileContent })
                });

                const data = await response.json();
                const loadingElement = document.getElementById(loadingId);

                if (response.ok) {
                    loadingElement.outerHTML = `
                        <div class="flex gap-4 max-w-3xl mx-auto items-start">
                            <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0 font-bold text-sm shadow-md">AI</div>
                            <div class="bg-slate-800/80 border border-slate-700/50 rounded-2xl p-4 shadow-sm message-content flex-1">${marked.parse(data.reply)}</div>
                        </div>
                    `;
                    document.querySelectorAll('pre code').forEach((block) => { hljs.highlightElement(block); });
                } else {
                    loadingElement.outerHTML = `<div class="flex gap-4 max-w-3xl mx-auto items-start"><div class="bg-red-950 border border-red-800 text-red-200 rounded-2xl p-4">Ошибка: ${data.error}</div></div>`;
                }
            } catch (error) {
                document.getElementById(loadingId).outerHTML = `<div class="flex gap-4 max-w-3xl mx-auto items-start"><div class="bg-red-950 border border-red-800 text-red-200 rounded-2xl p-4">Ошибка сети</div></div>`;
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function newChat() {
            document.getElementById('chat-container').innerHTML = `
                <div class="flex gap-4 max-w-3xl mx-auto items-start">
                    <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0 font-bold text-sm shadow-md">AI</div>
                    <div class="bg-slate-800/80 border border-slate-700/50 rounded-2xl p-4 shadow-sm message-content flex-1">
                        Новый чат начат. Чем могу помочь?
                    </div>
                </div>
            `;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    file_name = data.get("file_name", "")
    file_content = data.get("file_content", "")

    full_prompt = user_message
    if file_content:
        full_prompt = f"Пользователь прикрепил файл '{file_name}' со следующим содержимым:\n\n```\n{file_content}\n```\n\nВопрос/запрос пользователя: {user_message}"

    if not GEMINI_API_KEY:
        return jsonify({
            "reply": f"Привет! Облачный сервер работает. Вы написали: *\"{user_message}\"*" + (f" (и прикрепили файл: {file_name})" if file_name else "") + ". Чтобы активировать искусственный интеллект, добавьте переменную окружения `GEMINI_API_KEY` в настройках хостинга Render."
        })

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}]
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        res_data = response.json()

        if "candidates" in res_data:
            bot_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": bot_reply})
        else:
            error_msg = res_data.get("error", {}).get("message", "Неизвестная ошибка API")
            return jsonify({"error": error_msg}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
