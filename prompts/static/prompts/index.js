function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}


function startCount(el){
    let goal =  el.dataset.goal
    if (goal == 0) {
        return 0
    }
    let time = 2000 / goal

    let count = setInterval(() => {
        el.textContent++

        if(Number(el.textContent) === Number(goal)){
            clearInterval(count)
        }

    } , time)
}


function isInView(ele) {
    // Select element section
    let element = document.querySelector(ele);

    // testimonials offset top
    let elementTop = element.offsetTop;

    // testimonials outer hight
    let elementHeight = element.offsetHeight;

    //window height
    let windowHeight = this.innerHeight;

    // Window Y offset
    let windowScrollTop = this.pageYOffset;

    return windowScrollTop >= elementTop + elementHeight / 2  - windowHeight;
}
