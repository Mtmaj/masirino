import requests

class HomePage:
    def __init__(self,request):
        self.request = request
        self.query_valid = False
        self.lat = 0
        self.lon = 0
        self.gas_station = []
        self.gas_station_dict = []
        self.neshan_key = {
            "Api-Key" : "service.74202354f8874f589f12e5f3a1bdb8cf",
            'Content-Type': 'application/json'
        }
        self.search_url = "https://api.neshan.org/v1/search?term=پمپ بنزین&lat="
        self.distance_url = ""
    

    def create_distance_url(self):
        distance_url = "https://api.neshan.org/v1/distance-matrix?type=car&origins="+str(self.lat)+","+str(self.lon)+"&destinations="
        index = 0
        for gas_station in self.gas_station:
            distance_url += str(gas_station.lat)+','+str(gas_station.lon)
            index+=1
            if index < len(self.gas_station):
                distance_url+='%7C'
        self.distance_url = distance_url


    def main_page(self):
        self.query_valid = self.check_query()
        if self.query_valid:
            self.set_geolocation()
            self.get_gasStations()
            self.create_distance_url()
            self.get_gas_station_distance()
            if "sort" in self.request.GET:
                if self.request.GET['sort'] == 'time':
                    self.sort_by_time()
                else:
                    self.sort_by_distance()
            else:
                self.sort_by_distance()
            self.covert_dict()

            

    def covert_dict(self):
        print(self.gas_station)
        for item in self.gas_station:
            print(item.__dict__)
            self.gas_station_dict.append(item.__dict__)


    def get_gasStations(self):
        response = requests.request('GET',headers=self.neshan_key,url=self.search_url+str(self.lat)+'&lng='+str(self.lon))
        datas = response.json()
        for item in datas['items']:
            self.gas_station.append(GasStation(item))
    
    def get_gas_station_distance(self):
        response = requests.request('GET',self.distance_url,headers=self.neshan_key)
        datas = response.json()['rows'][0]['elements']
        index = 0;
        for item in datas:
            self.gas_station[index].time_distance = item['duration']['value'] // 60
            self.gas_station[index].distance = item['distance']['value'] // 1000
            index += 1

    
    def sort_by_time(self):
        for i in range(0,len(self.gas_station)):
            for j in range(i,len(self.gas_station)):
                if self.gas_station[i].time_distance > self.gas_station[j].time_distance:
                    temp =  self.gas_station[j]
                    self.gas_station[j] = self.gas_station[i]
                    self.gas_station[i] = temp

    def sort_by_distance(self):
        for i in range(0,len(self.gas_station)):
            for j in range(i,len(self.gas_station)):
                if self.gas_station[i].distance > self.gas_station[j].distance:
                    temp =  self.gas_station[j]
                    self.gas_station[j] = self.gas_station[i]
                    self.gas_station[i] = temp

    
    def set_geolocation(self):
        if self.query_valid:
            self.lat = self.request.GET['lat']
            self.lon = self.request.GET['lon']

    def check_query(self):
        if "lat" in self.request.GET and "lon" in self.request.GET :
            return True
        return False


class GasStation:
    def __init__(self,json_data):
        self.name = json_data['title']
        if "address" in json_data: 
            self.address = json_data['address']
            if len(json_data['address']) > 25:
                self.address = self.address[0:25] + '...'
            
        else:
            self.address = "آدرس پیدا نشد!"
        self.lat = json_data['location']['y']
        self.lon = json_data['location']['x']
        self.distance = 0
        self.time_distance = 0
    
    