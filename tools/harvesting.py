from yolox.data.datasets.coco_classes import COCO_CLASSES
from agent import DQN
from models import HarvestNet
from yolox.exp import get_exp
from environment import *
import torch
import argparse
import os
import keyboard
import winsound

from yolox.utils import get_model_info
from yolox2dqn import Predictor
from torchsummary import summary
from loguru import logger

def make_parser():
    parser = argparse.ArgumentParser("YOLOX Demo!")
    parser.add_argument("demo", default="image", help="demo type, eg. image, video and webcam")
    parser.add_argument("-expn", "--experiment-name", type=str, default=None)
    parser.add_argument("-n", "--name", type=str, default=None, help="model name")
    parser.add_argument("--path", default="./assets/dog.jpg", help="path to images or video")

    # exp file
    parser.add_argument(
        "-f",
        "--exp_file",
        default="yolox/exp/yolox_tiny_fish.py",
        type=str,
        help="pls input your experiment description file",
    )
    parser.add_argument("-c", "--ckpt", default="weights/best_tiny3.pth", type=str, help="ckpt for eval")
    parser.add_argument(
        "--device",
        default="gpu",
        type=str,
        help="device to run our model, can either be cpu or gpu",
    )
    parser.add_argument("--conf", default=0.25, type=float, help="test conf")
    parser.add_argument("--nms", default=0.45, type=float, help="test nms threshold")
    parser.add_argument("--tsize", default=640, type=int, help="test img size")
    parser.add_argument(
        "--fp16",
        dest="fp16",
        default=False,
        action="store_true",
        help="Adopting mix precision evaluating.",
    )
    parser.add_argument(
        "--legacy",
        dest="legacy",
        default=False,
        action="store_true",
        help="To be compatible with older versions",
    )
    parser.add_argument(
        "--fuse",
        dest="fuse",
        default=False,
        action="store_true",
        help="Fuse conv and bn for testing.",
    )
    parser.add_argument(
        "--trt",
        dest="trt",
        default=False,
        action="store_true",
        help="Using TensorRT model for testing.",
    )

    # DQN args
    parser.add_argument('--n_states', default=3, type=int)
    parser.add_argument('--n_actions', default=2, type=int)
    parser.add_argument('--step_tick', default=12, type=int)
    parser.add_argument('--model_dir', default='./weights/harvest_genshin_net.pth', type=str)

    return parser

def main(exp,args):
    def main(exp, args):
        if not args.experiment_name:
            args.experiment_name = exp.exp_name

        if args.trt:
            args.device = "gpu"

        logger.info("Args: {}".format(args))

        if args.conf is not None:
            exp.test_conf = args.conf
        if args.nms is not None:
            exp.nmsthre = args.nms
        if args.tsize is not None:
            exp.test_size = (args.tsize, args.tsize)

        model = exp.get_model()
        logger.info("Model Summary: {}".format(get_model_info(model, exp.test_size)))

        if args.device == "gpu":
            model.cuda()
            if args.fp16:
                model.half()  # to FP16
        model.eval()

        if not args.trt:
            if args.ckpt is None:
                ckpt_file = os.path.join(file_name, "best_ckpt.pth")
            else:
                ckpt_file = args.ckpt
            logger.info("loading checkpoint")
            ckpt = torch.load(ckpt_file, map_location="cpu")
            # load the model state dict
            model.load_state_dict(ckpt["model"])
            logger.info("loaded checkpoint done.")

        predictor = Predictor(model, exp, COCO_CLASSES, trt_file, decoder, args.device, args.fp16, args.legacy)

        agent = HarvestNet(args.n_states, args.n_actions)
        agent.load_state_dict(torch.load(args.model_dir))
        agent.eval()
        env=Environment(predictor=predictor)
        print('init ok')
        winsound.Beep(500, 500)
        keyboard.wait('r')
        for i_episode in range(args.n_episode):
            # play 400 episodes of cartpole game
            s = env.reset()
            ep_r = 0
            while True:
                a = agent.choose_action(s)
                if type(a) is np.ndarray:
                    # print("a is array")
                    a = a[0]
                if a is None:
                    # print("action is none")
                    a = 3
                s_, r, done = env.step(a)
                if done:
                    break




if __name__ == "__main__":
    args = make_parser().parse_args()
    exp = get_exp(args.exp_file, args.name)

    main(exp, args)
