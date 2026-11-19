// WhatsApp Web 浏览器助手（Claude in Chrome 的 javascript_tool 里执行；页面刷新后要重新注入）
// 2026-11-19 会话整理。用法见 工作流.md 第 4.3 / 6.5 节。

// 读当前聊天最后 n 条：ME=我方，CU=客户
window.hist=(n=10,L=260)=>document.querySelector('#main header').innerText.replace(/\n/g,' | ').slice(0,50)+'\n'+[...document.querySelectorAll('#main [role=row]')].map(r=>{const p=r.querySelector('[data-pre-plain-text]')?.getAttribute('data-pre-plain-text')||'';return (p?(/Evelyn/.test(p)?'ME ':'CU ')+(p.match(/\[(.*?)\]/)||['',''])[1].slice(0,13)+' ':'? ')+r.innerText.replace(/\n/g,' ').slice(0,L)}).filter(t=>t.length>14).slice(-n).join('\n');

// 多行插入：用 execCommand 插文字（emoji 1️⃣ 不会坏），行间用 Shift+Enter
window.insLines=async(lines)=>{const b=document.querySelector('#main footer [contenteditable=true]');b.focus();for(let i=0;i<lines.length;i++){if(i>0){b.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',keyCode:13,which:13,shiftKey:true,bubbles:true,cancelable:true}));await new Promise(r=>setTimeout(r,60));}if(lines[i])document.execCommand('insertText',false,lines[i]);await new Promise(r=>setTimeout(r,60));}return b.innerText.length};

// 安全填入：先核对聊天顶部包含 key、输入框为空，才填
window.put=async(key,lines)=>{const h=document.querySelector('#main header').innerText.replace(/\n/g,' | ');const box=document.querySelector('#main footer [contenteditable=true]');if(!h.includes(key)) return 'WRONG CHAT: '+h; if(box.innerText.trim()) return 'BOX NOT EMPTY'; await insLines(lines); return 'OK '+h+' | '+box.innerText.length+' chars'};
'hist / insLines / put ready';
