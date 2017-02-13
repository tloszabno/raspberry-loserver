var app = new Vue({
    el: '#losite',
    data: {
        humidex: {},
        day_info:{},
        errors: []
    },
    mounted: function() {
        this.fetch();
        setInterval(this.fetchHumidex, 60000*3); // 3min
        setInterval(this.fetchDayInfo, 10000); // 10sek
    },
    methods: {
        fetchDayInfo: function(){
            var self = this;
            $.get('day_info', function(response){
                if( response.ok ){
                    self.day_info = response.data;
                }else{
                    self.errors = self.errors.concat(response.errors);
                }
            });
        },
        fetchHumidex: function(){
            var self = this;
            $.get('humidex_info', function(response){
                if( response.ok ){
                    self.humidex = response.data;
                }else{
                    self.errors = self.errors.concat(response.errors);
                }
            });
        },
        fetch: function() {
            this.fetchDayInfo();
            this.fetchHumidex();
        }
    }
});
