var app = new Vue({
    el: '#losite',
    data: {
        humidex: {},
        day_info:{},
        wunder_today:[],
        wunder_todo_dom:[],
        errors: []
    },
    mounted: function() {
        this.fetch();
        setInterval(this.fetchHumidex, 60000*3); // 3min
        setInterval(this.fetchDayInfo, 10000); // 10sek
        setInterval(this.fetchWunderTasks, 30000); // 30sek
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
        fetchWunderTasks: function(){
            var self = this;
            $.get('wunderlist_todo_dom', function(response){
                if( response.ok ){
                    self.wunder_todo_dom = response.data;
                }else{
                    self.errors = self.errors.concat(response.errors);
                }
            });
            $.get('wunderlist_today', function(response){
                if( response.ok ){
                    self.wunder_today = response.data;
                }else{
                    self.errors = self.errors.concat(response.errors);
                }
            });
        },
        fetch: function() {
            this.fetchDayInfo();
            this.fetchHumidex();
            this.fetchWunderTasks();
        }

    }
});
