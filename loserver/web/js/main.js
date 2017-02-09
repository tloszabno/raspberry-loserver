var app = new Vue({
    el: '#losite',
    data: {
        message: "bla",
        humidex: {},
        errors: []
    },
    mounted: function() {
        this.fetch();
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
