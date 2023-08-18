function json_to_html_list(data_in_json) {
    let output = '';
    for (let item of data_in_json) {
        output += `
        <tr>
        <td>${item[0]}</td>
        <td>${item[1]}</td>
        <td>${item[2]} </td>
        <td>${item[3]}</td>
        <td>${item[4]}</td>
        <td>${item[5]}</td>
        <td>${item[6]}</td>
        <td>${item[7]}</td>
        </tr>`;
    }
    return output
}

function loadData() {
    fetch("http://127.0.0.1:5000/get_items")
        // the frontend is running on port: 3000 while backend on 5000, you need to specify that 
        .then(res => res.json())
        .then(res => {
            document.getElementById("items_display").innerHTML = json_to_html_list(res);
            
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

function sendDataNewTEST(){
    document.getElementById('jsonForm').addEventListener('submit', function(e){
        try {
            JSON.parse(document.querySelector('[name="jsonInput"]').value);
        } catch (error) {
            e.preventDefault();
            alert('Invalid JSON')
        }
    })
}

function validateJSON(){
    try {
        JSON.parse(document.querySelector('[name="jsonInput"]').value);
        return true;
    } catch (error) {
        alert('Invalid JSON provided!');
        return false;
    }
}

