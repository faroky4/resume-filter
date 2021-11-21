function deleteCandi(candiId){
    fetch('/delete-candi' , {
        methos: 'POST',
        body: JSON.stringify({candiId: candiId})
    }).then((_res)=> {
        window.location.href = "/candidates";
    })
}

