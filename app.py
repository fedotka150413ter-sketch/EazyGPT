import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT Клон - Универсальный Ассистент</title>
    <!-- Подключаем Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Подключаем шрифты Inter и иконки FontAwesome -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Подключаем Highlight.js для подсветки синтаксиса кода -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <!-- Подключаем Marked.js для рендеринга Markdown -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body { font-family: 'Inter', sans-serif; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
        .dark ::-webkit-scrollbar-thumb { background: #475569; }
        .code-block-wrapper { position: relative; margin: 1rem 0; border-radius: 0.5rem; overflow: hidden; background: #282c34; }
        .copy-code-btn { position: absolute; top: 0.5rem; right: 0.5rem; background: rgba(255,255,255,0.1); color: #fff; padding: 0.25rem 0.5rem; font-size: 0.75rem; border-radius: 0.25rem; transition: background 0.2s; }
        .copy-code-btn:hover { background: rgba(255,255,255,0.2); }
    </style>
</head>
<body class="h-full bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 flex flex-col md:flex-row overflow-hidden transition-colors duration-200">

    <div id="sidebar-overlay" class="fixed inset-0 bg-black/50 z-20 hidden md:hidden transition-opacity"></div>

    <aside id="sidebar" class="fixed inset-y-0 left-0 z-30 w-72 bg-slate-900 text-slate-200 flex flex-col transform -translate-x-full md:translate-x-0 md:static transition-transform duration-300 ease-in-out shadow-xl md:shadow-none">
        <div class="p-4 border-b border-slate-800 flex items-center justify-between">
            <button onclick="newChat()" class="flex-1 bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 py-2.5 px-4 rounded-xl flex items-center gap-3 text-sm font-medium transition shadow-sm">
                <i class="fa-solid fa-plus text-indigo-400"></i> Новый чат
            </button>
            <button onclick="toggleSidebar()" class="md:hidden ml-2 text-slate-400 hover:text-white p-2 rounded-lg">
                <i class="fa-solid fa-xmark text-lg"></i>
            </button>
        </div>

        <div id="chat-list" class="flex-1 overflow-y-auto p-3 space-y-1"></div>

        <div class="p-4 border-t border-slate-800 space-y-2">
            <button onclick="openCodeModal()" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 text-sm font-medium transition shadow-md shadow-indigo-600/20">
                <i class="fa-solid fa-globe"></i> Инструкция для Cloud
            </button>
            <div class="flex items-center justify-between text-xs text-slate-400 px-2 pt-2">
                <span><i class="fa-solid fa-circle text-emerald-500 text-[8px] mr-1"></i> Cloud Ready</span>
                <button onclick="toggleDarkMode()" class="hover:text-white p-1 rounded"><i class="fa-solid fa-moon dark:fa-sun"></i></button>
            </div>
        </div>
    </aside>

    <main class="flex-1 flex flex-col h-full relative bg-white dark:bg-slate-900">
        <header class="h-14 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 bg-white/80 dark:bg-slate-900/80 backdrop-blur z-10">
            <div class="flex items-center gap-3">
                <button onclick="toggleSidebar()" class="md:hidden text-slate-600 dark:text-slate-300 hover:text-slate-900 p-2 rounded-lg">
                    <i class="fa-solid fa-bars text-lg"></i>
                </button>
                <h1 id="current-chat-title" class="font-semibold text-sm md:text-base truncate">Новый диалог</h1>
            </div>
            <div class="flex items-center gap-2">
                <span class="text-xs bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-300 px-2.5 py-1 rounded-full font-medium">Gemini 3 Flash</span>
            </div>
        </header>

        <div id="chat-container" class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
            <div id="welcome-screen" class="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-4 py-12">
                <div class="w-16 h-16 rounded-2xl bg-indigo-600 text-white flex items-center justify-center text-3xl shadow-lg shadow-indigo-600/30">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <h2 class="text-2xl font-bold tracking-tight">Чем я могу помочь вам сегодня?</h2>
                <p class="text-sm text-slate-500 dark:text-slate-400">Этот облачный ИИ-ассистент доступен по постоянной ссылке в любой точке мира.</p>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full pt-4">
                    <button onclick="sendPreset('Напиши простой калькулятор на Python')" class="p-3 text-left text-xs bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-xl transition">
                        💻 Напиши скрипт на Python
                    </button>
                    <button onclick="sendPreset('Объясни квантовые вычисления простыми словами')" class="p-3 text-left text-xs bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-xl transition">
                        🚀 Объясни сложную тему
                    </button>
                </div>
            </div>
        </div>

        <div class="p-3 md:p-4 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
            <div class="max-w-4xl mx-auto relative flex items-end bg-slate-100 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 focus-within:border-indigo-500 transition shadow-sm">
                <textarea id="user-input" rows="1" placeholder="Введите сообщение..." class="w-full bg-transparent p-3 md:p-3.5 pr-12 text-sm focus:outline-none resize-none max-h-32 text-slate-800 dark:text-slate-100 placeholder-slate-400" onkeydown="handleKeyDown(event)" oninput="autoResize(this)"></textarea>
                <button id="send-btn" onclick="sendMessage()" class="absolute right-2 bottom-2 bg-indigo-600 hover:bg-indigo-500 text-white w-9 h-9 rounded-xl flex items-center justify-center transition shadow-md disabled:opacity-50">
                    <i class="fa-solid fa-arrow-up text-sm"></i>
                </button>
            </div>
            <p class="text-[10px] text-center text-slate-400 mt-2">Приложение развернуто в облаке и доступно по публичной ссылке.</p>
        </div>
    </main>

    <div id="code-modal" class="fixed inset-0 bg-black/60 z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white dark:bg-slate-900 rounded-2xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
            <div class="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
                <h3 class="font-bold text-base flex items-center gap-2"><i class="fa-solid fa-globe text-indigo-500"></i> Руководство по размещению в интернете</h3>
                <button onclick="closeCodeModal()" class="text-slate-400 hover:text-slate-600 dark:hover:text-white p-1 rounded-lg"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            <div class="flex-1 overflow-y-auto p-6 space-y-4 text-sm text-slate-600 dark:text-slate-300">
                <div class="bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-900 p-4 rounded-xl">
                    <h4 class="font-bold text-indigo-900 dark:text-indigo-300 mb-1">Как выложить этот сайт в интернет бесплатно?</h4>
                    <p class="text-xs text-indigo-700 dark:text-indigo-400">Используйте облачный сервис Render.com (или аналоги)</p>
                </div>
                <ol class="list-decimal list-inside space-y-2 text-xs md:text-sm">
                    <li>Создайте публичный репозиторий на <b>GitHub</b> и загрузите туда два файла: <code class="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">app.py</code> и <code class="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">requirements.txt</code></li>
                    <li>Зарегистрируйтесь на <a href="https://render.com" target="_blank" class="text-indigo-500 underline">Render.com</a> (можно войти через GitHub).</li>
                    <li>Нажмите кнопку <b>New +</b> -> <b>Web Service</b> и выберите ваш репозиторий.</li>
                    <li>Укажите параметры:<br>
                        - Build Command: <code class="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">pip install -r requirements.txt</code><br>
                        - Start Command: <code class="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">gunicorn app:app</code>
                    </li>
                    <li>В настройках (Environment) добавьте переменную <code class="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">GEMINI_API_KEY</code> со своим ключом от Gemini.</li>
                    <li>Нажмите <b>Create Web Service</b> — через минуту вы получите готовую ссылку вида <code class="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded font-mono">https://your-app.onrender.com</code>!</li>
                </ol>
            </div>
            <div class="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex justify-end">
                <button onclick="closeCodeModal()" class="bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-800 dark:text-white px-4 py-2 rounded-xl text-xs font-medium transition">Закрыть</button>
            </div>
        </div>
    </div>

    <script>
        let chats = JSON.parse(localStorage.getItem('chat_history') || '[]');
        let currentChatId = null;

        document.addEventListener('DOMContentLoaded', () => {
            if (chats.length === 0) {
                newChat();
            } else {
                loadChat(chats[0].id);
            }
            renderChatList();
            
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        return hljs.highlight(code, { language: lang }).value;
                    }
                    return hljs.highlightAuto(code).value;
                }
            });
        });

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('-translate-x-full');
            document.getElementById('sidebar-overlay').classList.toggle('hidden');
        }

        function toggleDarkMode() {
            document.documentElement.classList.toggle('dark');
        }

        function newChat() {
            const newId = 'chat_' + Date.now();
            chats.unshift({ id: newId, title: 'Новый диалог', messages: [] });
            saveChats();
            loadChat(newId);
            renderChatList();
            if (window.innerWidth < 768) toggleSidebar();
        }

        function loadChat(id) {
            currentChatId = id;
            const chat = chats.find(c => c.id === id);
            if (!chat) return;

            document.getElementById('current-chat-title').textContent = chat.title;
            const container = document.getElementById('chat-container');
            
            if (chat.messages.length === 0) {
                container.innerHTML = `
                    <div id="welcome-screen" class="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-4 py-12">
                        <div class="w-16 h-16 rounded-2xl bg-indigo-600 text-white flex items-center justify-center text-3xl shadow-lg shadow-indigo-600/30">
                            <i class="fa-solid fa-robot"></i>
                        </div>
                        <h2 class="text-2xl font-bold tracking-tight">Чем я могу помочь вам сегодня?</h2>
                        <p class="text-sm text-slate-500 dark:text-slate-400">Этот облачный ИИ-ассистент доступен по постоянной ссылке в любой точке мира.</p>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full pt-4">
                            <button onclick="sendPreset('Напиши простой калькулятор на Python')" class="p-3 text-left text-xs bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-xl transition">💻 Напиши скрипт на Python</button>
                            <button onclick="sendPreset('Объясни квантовые вычисления простыми словами')" class="p-3 text-left text-xs bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 rounded-xl transition">🚀 Объясни сложную тему</button>
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML = '';
                chat.messages.forEach(msg => appendMessageUI(msg.role, msg.content, false));
            }
            renderChatList();
        }

        function renderChatList() {
            const listEl = document.getElementById('chat-list');
            listEl.innerHTML = '';
            chats.forEach(chat => {
                const isActive = chat.id === currentChatId;
                const div = document.createElement('div');
                div.className = `group flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium cursor-pointer transition ${isActive ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`;
                div.innerHTML = `
                    <div class="flex items-center gap-3 truncate flex-1" onclick="loadChat('${chat.id}')">
                        <i class="fa-regular fa-message text-slate-400"></i>
                        <span class="truncate">${chat.title}</span>
                    </div>
                    <button onclick="deleteChat(event, '${chat.id}')" class="opacity-0 group-hover:opacity-100 hover:text-red-400 p-1 transition"><i class="fa-solid fa-trash-can"></i></button>
                `;
                listEl.appendChild(div);
            });
        }

        function deleteChat(e, id) {
            e.stopPropagation();
            chats = chats.filter(c => c.id !== id);
            saveChats();
            if (chats.length === 0) newChat();
            else if (currentChatId === id) loadChat(chats[0].id);
            else renderChatList();
        }

        function saveChats() {
            localStorage.setItem('chat_history', JSON.stringify(chats));
        }

        function autoResize(el) {
            el.style.height = 'auto';
            el.style.height = (el.scrollHeight) + 'px';
        }

        function handleKeyDown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        }

        function sendPreset(text) {
            document.getElementById('user-input').value = text;
            sendMessage();
        }

        async function sendMessage() {
            const inputEl = document.getElementById('user-input');
            const text = inputEl.value.trim();
            if (!text) return;

            inputEl.value = '';
            inputEl.style.height = 'auto';

            const welcome = document.getElementById('welcome-screen');
            if (welcome) welcome.remove();

            appendMessageUI('user', text, true);
            
            const loadingId = 'loading_' + Date.now();
            appendLoadingUI(loadingId);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, chat_id: currentChatId })
                });
                const data = await response.json();
                
                removeLoadingUI(loadingId);

                if (data.reply) {
                    appendMessageUI('assistant', data.reply, true);
                    const chat = chats.find(c => c.id === currentChatId);
                    if (chat && chat.title === 'Новый диалог') {
                        chat.title = text.length > 25 ? text.substring(0, 25) + '...' : text;
                        document.getElementById('current-chat-title').textContent = chat.title;
                        renderChatList();
                    }
                } else {
                    appendMessageUI('assistant', 'Ошибка: ' + (data.error || 'Не удалось получить ответ'), true);
                }
            } catch (err) {
                removeLoadingUI(loadingId);
                appendMessageUI('assistant', 'Ошибка соединения с сервером.', true);
            }
        }

        function appendMessageUI(role, content, save = true) {
            const container = document.getElementById('chat-container');
            const isUser = role === 'user';
            
            if (save && currentChatId) {
                const chat = chats.find(c => c.id === currentChatId);
                if (chat) {
                    chat.messages.push({ role, content });
                    saveChats();
                }
            }

            const wrapper = document.createElement('div');
            wrapper.className = `flex gap-4 max-w-4xl mx-auto w-full ${isUser ? 'justify-end' : 'justify-start'} py-2`;

            const avatar = isUser ? '' : `
                <div class="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-md">
                    <i class="fa-solid fa-robot text-xs"></i>
                </div>
            `;

            const parsedContent = isUser ? escapeHtml(content) : marked.parse(content);

            const bubble = document.createElement('div');
            bubble.className = `max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${isUser ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 w-full'}`;
            
            if (isUser) {
                bubble.textContent = content;
            } else {
                bubble.innerHTML = parsedContent;
                bubble.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                    const pre = block.parentElement;
                    const btn = document.createElement('button');
                    btn.className = 'copy-code-btn';
                    btn.innerHTML = '<i class="fa-regular fa-copy mr-1"></i> Копировать';
                    btn.onclick = () => {
                        navigator.clipboard.writeText(block.textContent);
                        btn.innerHTML = '<i class="fa-solid fa-check mr-1"></i> Скопировано!';
                        setTimeout(() => btn.innerHTML = '<i class="fa-regular fa-copy mr-1"></i> Копировать', 2000);
                    };
                    pre.style.position = 'relative';
                    pre.appendChild(btn);
                });
            }

            if (isUser) wrapper.appendChild(bubble);
            else {
                wrapper.innerHTML = avatar;
                wrapper.appendChild(bubble);
            }

            container.appendChild(wrapper);
            container.scrollTop = container.scrollHeight;
        }

        function appendLoadingUI(id) {
            const container = document.getElementById('chat-container');
            const wrapper = document.createElement('div');
            wrapper.id = id;
            wrapper.className = 'flex gap-4 max-w-4xl mx-auto w-full justify-start py-2';
            wrapper.innerHTML = `
                <div class="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shrink-0 shadow-md">
                    <i class="fa-solid fa-robot text-xs"></i>
                </div>
                <div class="bg-slate-100 dark:bg-slate-800 rounded-2xl px-4 py-3 flex items-center gap-1.5 text-slate-400">
                    <span class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce"></span>
                    <span class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.2s]"></span>
                    <span class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.4s]"></span>
                </div>
            `;
            container.appendChild(wrapper);
            container.scrollTop = container.scrollHeight;
        }

        function removeLoadingUI(id) {
            const el = document.getElementById(id);
            if (el) el.remove();
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        function openCodeModal() { document.getElementById('code-modal').classList.remove('hidden'); }
        function closeCodeModal() { document.getElementById('code-modal').classList.add('hidden'); }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Пустое сообщение'}), 400

    api_key = os.environ.get('GEMINI_API_KEY', '')
    
    try:
        import requests
        if api_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": user_message}]}]
            }
            res = requests.post(url, json=payload, timeout=30)
            res_data = res.json()
            candidate = res_data.get('candidates', [{}])[0]
            reply_text = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'Извините, не удалось получить ответ от модели.')
        else:
            reply_text = f"Привет! Облачный сервер работает. Вы написали: *\"{user_message}\"*. Чтобы активировать искусственный интеллект, добавьте переменную окружения `GEMINI_API_KEY` в настройках хостинга."
            
        return jsonify({'reply': reply_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
