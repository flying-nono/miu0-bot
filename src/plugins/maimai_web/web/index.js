//在 DOM 全部加载完毕后才开始调用。

document.addEventListener('DOMContentLoaded', function() {
    let form = document.querySelector('form');
    let button1 = document.querySelector('#button1');
    
    button1.addEventListener('click', ()=>{
        form.action = 'http://121.4.27.82:25565/b50/image';
    });
});

