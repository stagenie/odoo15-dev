function change_input_po(params) {
    let id = params.className
    let _quantity = params.getElementsByTagName("span")[0];
    if (_quantity) {
        params.innerHTML = `<input class='text-center px-1 mx-1' value='${_quantity.innerHTML}' id='inputid${id}' onchange='change_quantity_po(${id},${_quantity.innerHTML},this)' min='0' max='999999999' type='number'/>`;
    }
}

const change_quantity_po = async (id, _quantity, tag) => {
    let qtyspantag = document.createElement("span");
    if (Number(tag.value) < 0) {
        tag.value = '0.00'
        return
    }
    let data = sessionStorage.getItem("current_action")
    if (data) {
        data = JSON.parse(data)
        let _purchase_id = data.context.purchase_id;
        // let uom_category = await $.ajax({
        //     url: "/getuom_po",
        //     method: "GET",
        //     dataType: 'json',
        //     data: { product_id: id }
        // });
        // if(uom_category["uom_category"] == 'unit'){
        //     tag.value = Math.round(tag.value);
        //     tag.value = tag.value.concat('.00')
        // }
        $.ajax({
            url: "/qtyupdatecart_po",
            method: "GET",
            dataType: 'json',
            data: { quantity: Number(tag.value), product_id: id, purchase_id: _purchase_id }
        });
        qtyspantag.innerText = tag.value;
        tag.replaceWith(qtyspantag);
    }
}
