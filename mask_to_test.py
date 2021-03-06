from network import *
import cv2
import glob



def test(args, sess, model):
    # saver
    saver = tf.train.Saver()
    last_ckpt = tf.train.latest_checkpoint(args.checkpoints_path)
    saver.restore(sess, last_ckpt)
    ckpt_name = str(last_ckpt)
    print("Loaded model file from " + ckpt_name)
    #read the images 
    paths = glob.glob('./testimage_2016/*')
    step = 0
    for path in paths:
        img = cv2.imread(path)#read in the path of the test image 
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = cv2.resize(img, (args.input_height, args.input_width))
        orig_test = cv2.resize(img, (args.input_height, args.input_width)) / 127.5 - 1
        # orig_test = cv2.resize(img, (args.input_height, args.input_width))/127.5 - 1

        ##### the mask process
        mask = np.zeros(img.shape)
        color = (255,255,255)
        size = np.random.randint(15 , high=20 ,size=2)
        x= np.random.randint(10 , high =54 - size[0], size = 1)
        y= np.random.randint(10 , high =54 - size[1], size = 1) #the minum of x and y
        img = cv2.rectangle(img,(x[0],y[0]),(x[0]+size[0],y[0]+size[1]),color,-1)
        mask = cv2.rectangle(mask,(x[0],y[0]),(x[0]+size[0],y[0]+size[1]),color,-1)

        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        test_img = cv2.resize(img, (args.input_height, args.input_width)) / 127.5 - 1
        test_mask = cv2.resize(mask, (args.input_height, args.input_width)) / 255.0
        test_img = (test_img * (1-test_mask)) + test_mask

        test_img = np.tile(test_img[np.newaxis,...], [args.batch_size,1,1,1])
        mask = np.tile(test_mask[np.newaxis,...], [args.batch_size,1,1,1])

        ####save the images after erase process

        # print(orig_test.shape) #(64, 64, 3)
        orig_test = np.tile(orig_test[np.newaxis, ...], [args.batch_size, 1, 1, 1])  # transfer the format from(64, 64, 3)to(64, 64, 64, 3)
        # print(orig_test.shape) #(64, 64, 64, 3)
        orig_test = orig_test.astype(np.float32)  # orig_test are 4-dimention vector 1111
        # print(orig_test.shape) #(64, 64, 64, 3)
        # print(test_img.shape) #(64, 64, 64, 3)
        test_img = test_img.astype(np.float32)

        print("Testing ...")

        res_img = sess.run(model.test_res_imgs, feed_dict={model.single_orig: orig_test,
                                                           model.single_test: test_img,
                                                           model.single_mask: mask})

        orig_test = cv2.cvtColor(orig_test[0], cv2.COLOR_BGR2RGB)
        test_img = cv2.cvtColor(test_img[0], cv2.COLOR_BGR2RGB)
        res_img = cv2.cvtColor(res_img[0], cv2.COLOR_BGR2RGB)

        cv2.imwrite("./test_result_orig/" + str(step) + "_orig.jpg", (orig_test + 1) * 127.5)
        cv2.imwrite("./test_result_test/" + str(step) + "_test.jpg", (test_img + 1) * 127.5)
        cv2.imwrite("./test_result_res/" + str(step) + "_res.jpg", (res_img + 1) * 127.5)
        # cv2.imshow("result", (res_img + 1) * 127.5)
        # cv2.waitKey(0)
        step+=1
        print(step)
    print("done.")


def main(_):
    run_config = tf.ConfigProto()
    run_config.gpu_options.allow_growth = True

    with tf.Session(config=run_config) as sess:
        model = network(args)

        print('Start Testing...')
        test(args, sess, model)


main(args)
