function add_reversed_data_from_js(){
    let list_data2 = list_data.push("test_input_from_js");

    document.getElementById("output_from_js").innerHTML = "from_js:" + list_data2;
}

// function select_due_js(){
//     var select_due = document.getElementById("due").value = {{ due_uni | tojson}};
//     console.log(select_due);
//     var radio = document.getElementsByName("period");
//     var my_period = {{ period | tojson }};
//     for(var i = 0; i < radio.length; i++){
//         // console.log(radio[i]);
//         if(radio[i].value == my_period){
//             // document.getElementsByName("day").checked = false;
//             // document.getElementsByName(my_period).checked == true;
//             console.log("選択された値：", radio[i].value);
//         }
//     }
// };