var app = new Vue({
    el: '#losite',
    data: {
        message: "bla",
        humidex: {},
        current_date: "10.02.17",
        current_time: "19:25",
        day_messages: ["Imieniny Taty", "Urodziny Mamy"],
        errors: []
    },
    mounted: function() {
        this.fetch();
        hideAddressBar();
    },
    methods: {
        fetch: function() {
            var self = this;
            $.get('humidex_info', function(response){
                if( response.ok ){
                    self.humidex = response.data;
                }else{
                    self.errors = response.errors;
                }
            });
        }
    }
});
