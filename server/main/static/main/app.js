function get_frames(){
    let frames = document.querySelectorAll('.frame')

    frames.forEach(point => {
        img = point.querySelector('.img')
        new_img = `<img class='img' src="${img.src}" alt="">`
        point.insertAdjacentHTML('beforeend', new_img)
    }) 
}

setInterval(() => get_frames(), 2000)