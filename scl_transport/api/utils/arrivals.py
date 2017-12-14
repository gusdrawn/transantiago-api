

class NextArrivals(object):
    def __init__(self, live_arrivals, scheduled_arrivals):
        self.live_arrivals = live_arrivals
        self.scheduled_arrivals = scheduled_arrivals

    def get_base_dict(self):
        return {
            'route_id': None,
            'is_live': False,
            'calculated_at': '',
            'bus_distance': None,
            'bus_plate_number': None,
            'arrival_estimation': ''

        }

    def _already_in_results(self, route_id, results):
        for r in results:
            if r['route_id'] == route_id:
                return True
        return False

    def get_item(self, route_id, index, data):
        item_index = 0
        for item in data:
            if item['route_id'] == route_id:
                if item_index == index:
                    return item
                else:
                    item_index += 1
        return None

    def get_combined_results(self):
        results = []
        # 1: augment live data
        for live_arrival in self.live_arrivals['routes']:
            if live_arrival['code'] in ('00', '01', '9', '09', '10', '11', '12'):  # live data
                item = self.get_base_dict()
                # fill with live data
                item['is_live'] = True
                item['route_id'] = live_arrival['route_id']
                item['bus_distance'] = live_arrival['bus_distance']
                item['bus_plate_number'] = live_arrival['bus_plate_number']
                item['arrival_estimation'] = live_arrival['route_arrival_prediction'] or live_arrival['message']
                item['calculated_at'] = live_arrival['calculated_at']

                # fill with schedule data
                """
                if not self._already_in_results(live_arrival['route_id'], results):
                    scheduled_item = self.get_item(item['route_id'], 0, self.scheduled_arrivals)
                else:
                    scheduled_item = self.get_item(item['route_id'], 1, self.scheduled_arrivals)
                if scheduled_item:
                    item['trip_id'] = scheduled_item['trip_id']
                    item['headway_secs'] = scheduled_item['headway_secs']
                """
                results.append(item)

        # 2: fill with scheduled arrivals
        """
        scheduled_results = []
        for scheduled_arrival in self.scheduled_arrivals:
            for r in results:
                if scheduled_arrival['route_id'] == r['route_id']:
                    break
            else:
                item = self.get_base_dict()
                item['route_id'] = scheduled_arrival['route_id']
                item['trip_id'] = scheduled_arrival['trip_id']
                item['headway_secs'] = scheduled_arrival['headway_secs']
                item['calculated_at'] = scheduled_arrival['calculated_at']
                item['arrival_estimation'] = scheduled_arrival['arrival_prediction_message']
                scheduled_results.append(item)

        results.extend(scheduled_results)
        """

        # 3: @@TODO: how to sort?
        return results
