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
        <td>${item[8]}</td>
        <td>${item[9]}</td>
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
            const table = document.getElementById("items_display");
            const count = table.rows.length;
            const countDisplay = document.getElementById("item_count");
            countDisplay.textContent = "identifier: " + count;
            
        });
         
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
function sortTable(columnIndex) {
    const table = document.getElementById("items_display");
    let rows = Array.from(table.rows);
    const isNumeric = inferColumnType(rows, columnIndex);

    // Sort rows array
    rows.sort((a, b) => {
        const cellA = a.cells[columnIndex].innerText;
        const cellB = b.cells[columnIndex].innerText;

        if (isNumeric) {
            return parseInt(cellA, 10) - parseInt(cellB, 10);
        } else {
            return cellA.localeCompare(cellB);
        }
    });

    // Append rows in the new order to the table
    for (let row of rows) {
        table.appendChild(row);
    }
}

function inferColumnType(rows, columnIndex) {
    // Check a few rows to infer data type
    for (let i = 0; i < rows.length && i < 5; i++) {
        const cellValue = rows[i].cells[columnIndex] && rows[i].cells[columnIndex].innerText.trim();
        if (cellValue && !isNaN(cellValue) && Number.isInteger(+cellValue)) {
            return true; // Numeric (Integer)
        }
    }
    return false; // String
}

document.addEventListener('DOMContentLoaded', function() {
    const headers = document.querySelectorAll("th");
    headers.forEach((header, index) => {
        header.addEventListener("click", function() {
            sortTable(index);
        });
    });
});
