$(function(){


    let datePicker = document.getElementById('datePicker');
    let picker = new Lightpick({
        field: datePicker,
        autoclose: false,
        hideOnBodyClick: true,
        repick: true,
        onSelect: function(date){
            datePicker.value = date.format('D MMMM YYYY');
            window.location.href = "dashboard.php?day="+datePicker.value;

        },
        onClose: function(){
          datePicker.value = "Antonio"
        }
    });




});
