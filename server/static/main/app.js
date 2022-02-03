function get_frames(){
    let frames = document.querySelectorAll('.frame')

    frames.forEach(point => {
        img = point.querySelector('.img')
        new_img = `<img class='img' src="${img.src}" alt="frame">`
        point.innerHTML = new_img
    }) 
}

while (true){
    setTimeout(get_frames, 0.5)
}

