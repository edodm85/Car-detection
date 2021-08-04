import cv2
import imutils as imutils
import numpy as np

from VehicleTracker import VehicleTracker



# TEXT
name = 'Edodm85'
font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 2
fontColor = (255,255,255)
lineType = 2

# ROI
# l'immagine originale è da 1920x1080 i primi 160 pixel in altezza sono riservati all'intestazione
# l'immgine elabirata è da 1920x(1080-160) = 1920x920 con x,y = 0,160
roi = (0, 160, 1920, (1080-160))            # x, y, w, h

# CAR
car_size = (120, 300)

detec = []
pos_lin_h = 350
offset = 6




def main():
    # Create a VideoCapture object and read from input file
    cap = cv2.VideoCapture('DRONE-SURVEILLANCE-CONTEST-VIDEO.mp4')

    # Check if camera opened successfully
    if (cap.isOpened() == False):
        print("Unable to read camera feed")

    # Default resolutions of the frame are obtained.The default resolutions are system dependent.
    # We convert the resolutions from float to integer.
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    # Define the codec and create VideoWriter object.The output is stored in 'output.avi' file.
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

    car_count = 0
    count = 0
    frame_counter = 0

    # Tracker
    tracker = VehicleTracker()

    list_ID = []

    while (True):
        ret, frame = cap.read()

        if ret == True:
            frame_counter += 1

            if frame_counter > 30:
                pos_lin_h = 450
            else:
                pos_lin_h = 350

            array_bb = []
            frame_h, frame_w, ch = frame.shape

            # add text to image
            cv2.putText(frame, name, (848,100), font, fontScale, fontColor, lineType)
            # add car counter to image
            cv2.putText(frame, str(car_count), (1750, 100), font, fontScale, fontColor, lineType)

            # Apply ROI
            image_ROI = frame[roi[1]:frame_h, 0:frame_w, :]

            # rgb threshold
            image_th = cv2.inRange(image_ROI, (50, 100, 190), (160, 190, 255))     #99 - ID 338

            # Taking a matrix of size 5 as the kernel
            kernel = np.ones((5, 5), np.uint8)
            img_dilation = cv2.dilate(image_th, kernel, iterations=5)
            img_erosion = cv2.erode(img_dilation, kernel, iterations=1)

            # inversion
            image_out = cv2.bitwise_not(img_erosion)

            # Returns a list of objects
            contours = cv2.findContours(image_out.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # Converts it
            contours = imutils.grab_contours(contours)

            # line car counter
            cv2.line(frame, (0, pos_lin_h), (1920, pos_lin_h), (176, 130, 39), 2)
            # Loops over all objects found
            for contour in contours:
                # Bounding box
                (x, y, w, h) = cv2.boundingRect(contour)
                y = y + roi[1]
                bb_double = False
                h_original = 0

                if ((h > car_size[1] / 2) and (w > car_size[0] / 2)):

                    if (h > car_size[1]):
                        h_original = h
                        h = car_size[1]
                        bb_double = True


                    if (w > car_size[0]):
                        x = x + (w - car_size[0])
                        w = car_size[0]

                    if not((y == roi[1]) or (y + h == roi[1] + roi[3])):
                        array_bb.append([x, y, w, h])
                    else:
                        if bb_double:
                            array_bb.append([x, y, w, h_original])

            output = tracker.update_bb(array_bb)


            for bb in output:
                x, y, w, h, cx, cy, id = bb

                # draw centroid
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                # write ID
                cv2.putText(frame, str(id), (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                # draw BoundingBox Green
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # cars counter
                if (cy < (pos_lin_h + offset)) and (cy > (pos_lin_h - offset)):

                    bl_new_id = False
                    if not (id in list_ID):
                        bl_new_id = True
                        list_ID.append(id)

                    if bl_new_id:
                        car_count += 1
                        cv2.line(frame, (0, pos_lin_h), (1920, pos_lin_h), (0, 127, 255), 3)
                        print("BB: (" + str(cx) + "," + str(cy) + ") car_count: " + str(car_count) + " ID: "+ str(id))



            processing_out = frame

            # save images
            cv2.imwrite("Images/frame%d.jpg" % count, processing_out)
            count += 1

            # Write the frame into the file 'output.avi'
            out.write(frame)

            # Display the resulting frame
            #cv2.imshow('frame', frame)

            # Press Q on keyboard to stop recording
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Break the loop
        else:
            break

    # When everything done, release the video capture and video write objects
    cap.release()
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()





if __name__ == "__main__":
    main()
