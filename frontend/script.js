function json_to_html_list(data_in_json) {
    let output = "<tr>";
    for (let item of data_in_json) {
        output += `<td>${item[0]} -- ${item[1]} -- ${item[2]} -- ${item[3]} -- ${item[4]} -- ${item[5]} -- ${item[6]}</td>`;
    }
    output += "</tr>";
    return output
}

function loadData() {
    fetch("http://127.0.0.1:5000/get_items")
    // the frontend is running on port: 3000 while backend on 5000, you need to specify that 
    .then(res => res.json())
    .then(res => {
        document.getElementById("data_display").innerHTML = json_to_html_list(res);
        //console.log(res);    
    })
}

function sendData() {
    const itemName = document.getElementById("item_name").value;
    const itemPrice = document.getElementById("item_price").value;
    console.log(itemName); 
    console.log(itemPrice); 

    const data = {
        item: itemName,
        price: itemPrice
    }

    fetch('http://127.0.0.1:5000/send_items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)

    })

}