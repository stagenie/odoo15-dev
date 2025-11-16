console.log("loaded")

function change_input_so(params) {
    let id = params.className
    console.log(id)
    let _quantity = params.getElementsByTagName("span")[0];
    if (_quantity) {
        params.innerHTML = `<input class='text-center px-1 mx-1' value='${_quantity.innerHTML}'  id='inputid${id}' onchange='change_quantity_so("${id}","${_quantity.innerHTML}",event)' min='0' max='999999999' type='number'/>`;
    }
}

const change_quantity_so = async (id, _quantity, event) => {
    let qtyspantag = document.createElement("span");
    let tag = event.target
    console.log(tag.value, "tag value")
    if (Number(tag.value) < 0) {
        console.log("changing")
        tag.value = '0.00'
        // qtyspantag.innerText = '0';
        // tag.replaceWith(qtyspantag);
        // return;
    }
    console.log(tag.value, "tag value after")

    let data = JSON.parse(sessionStorage.getItem("current_action"));
    if (data) {
        // data = JSON.parse(data);
        console.log(data, "data");
        let _sale_id = data.context.sale_id;
        // let uom_category = await $.ajax({
        //     url: "/getuom_so",
        //     method: "GET",
        //     dataType: 'json',
        //     data: { quantity: Number(tag.value), product_id: id, sale_id: _sale_id }
        // });
        // console.log(uom_category, "uom category");
        // if(uom_category["uom_category"] == 'unit'){
        //     tag.value = Math.round(tag.value);
        //     tag.value = tag.value.concat('.00')
        // }
        $.ajax({
            url: "/qtyupdatecart_so",
            method: "GET",
            dataType: 'json',
            data: { quantity: Number(tag.value), product_id: id, sale_id: _sale_id }
        });
        qtyspantag.innerText = tag.value;
        tag.replaceWith(qtyspantag);
    }
}
