import math


class VehicleTracker:
    def __init__(self):
        # vehicle ID
        self.id_vehicle = 0
        self.array_centroid = {}


    def get_centroid(self, x, y, w, h):
        x1 = int(w / 2)
        y1 = int(h / 2)

        cx = x + x1
        cy = y + y1

        return (cx, cy)


    def update_bb(self, obj):
        bb_array = []

        for bb in obj:
            new_object = True

            x, y, w, h = bb
            # centroid
            cx, cy = self.get_centroid(x, y, w, h)

            for id, pt in self.array_centroid.items():
                if (cx >= pt[0] - 20) and (cx <= pt[0] + 20):
                    # So Euclidean length from the origin is calculated by sqrt(x1*x1 + x2*x2 +x3*x3 .... xn*xn)
                    dist = math.sqrt((cx - pt[0])**2 + (cy - pt[1])**2)

                    if dist < 50:
                        self.array_centroid[id] = (cx, cy)
                        bb_array.append([x, y, w, h, cx, cy, id])
                        new_object = False
                        break

            # new object
            if new_object:
                self.array_centroid[self.id_vehicle] = (cx, cy)
                bb_array.append([x, y, w, h, cx, cy, self.id_vehicle])
                #print([x, y, w, h, cx, cy, self.id_vehicle])
                self.id_vehicle += 1


        self.array_centroid = {}
        for temp in bb_array:
            _, _, _, _, cx, cy, id = temp
            self.array_centroid[id] = (cx, cy)  # center

        return bb_array
