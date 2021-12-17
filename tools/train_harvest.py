#from yolox.data.datasets.fish_classes import FISH_CLASSES
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
        default=None,
        type=str,
        help="pls input your experiment description file",
    )
    parser.add_argument("-c", "--ckpt", default=None, type=str, help="ckpt for eval")
    parser.add_argument(
        "--device",
        default="cpu",
        type=str,
        help="device to run our model, can either be cpu or gpu",
    )
    parser.add_argument("--conf", default=0.3, type=float, help="test conf")
    parser.add_argument("--nms", default=0.3, type=float, help="test nms threshold")
    parser.add_argument("--tsize", default=None, type=int, help="test img size")
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
    parser.add_argument('--batch_size', default=32, type=int)
    parser.add_argument('--n_states', default=2, type=int)
    parser.add_argument('--n_actions', default=5, type=int)
    #parser.add_argument('--model_dir', default='./weights/fish_genshin_net.pth', type=str)
    parser.add_argument('--step_tick', default=12, type=int)
    parser.add_argument('--n_episode', default=400, type=int)
    parser.add_argument('--save_dir', default='./output_harvest', type=str)

    return parser

def get_predict(exp,args):
    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)
    #file_name = os.path.join(exp.output_dir, args.experiment_name)
    net = HarvestNet(in_channel=args.n_states, out_channel=args.n_actions)
    # if args.resume:
    #     net.load_state_dict(torch.load(args.resume))

    agent = DQN(net, args.batch_size, args.n_states, args.n_actions, memory_capacity=1000)

    model = exp.get_model()
    # print(model)
    logger.info("Model Summary: {}".format(get_model_info(model, exp.test_size)))
    if args.device == "gpu":
        model.cuda()
        if args.fp16:
            model.half()  # to FP16
    model.eval()

    if not args.trt:
        ckpt_file = args.ckpt
        logger.info("loading checkpoint")
        ckpt = torch.load(ckpt_file, map_location="cpu")
        # load the model state dict
        model.load_state_dict(ckpt["model"])
        logger.info("loaded checkpoint done.")
    # summary(model,input_size=(1,3,640,640))
    predictor = Predictor(model, exp, COCO_CLASSES, trt_file=None, decoder=None, device='gpu')
    env = Environment(predictor=predictor)

    return env,agent,predictor,net

if __name__ == '__main__':
    args = make_parser().parse_args()
    exp = get_exp(args.exp_file, args.name)
    env, agent, predictor, net=get_predict(exp,args)
    # Start training
    print("\nCollecting experience...")
    net.train()
    winsound.Beep(500, 500)
    keyboard.wait('r')
    for i_episode in range(args.n_episode):
        # play 400 episodes of cartpole game
        s = env.reset()
        ep_r = 0
        while True:
            # take action based on the current state
            #print("state here")
            print(s)
            #s=env.shape_state()
            a = agent.choose_action(s)
            # obtain the reward and next state and some other information
            #print("action here")
            print(a)
            if type(a) is np.ndarray:
                #print("a is array")
                a=a[0]
            if a is None:
                #print("action is none")
                a=3
            s_, r, done = env.step(a)

            # store the transitions of states
            agent.store_transition(s, a, r, s_)
            ep_r += r
            print("agent count here")
            print(agent.memory_counter)
            print(agent.memory_capacity)
            # if the experience repaly buffer is filled, DQN begins to learn or update
            # its parameters.
            if agent.memory_counter > agent.memory_capacity:
                print("we have train here !!!")
                agent.train_step()
                if done:
                    print('Ep: ', i_episode, ' |', 'Ep_r: ', ep_r.int())

            if done:
                # if game is over, then skip the while loop.
                break
            # use next state to update the current state.
            s = s_
        torch.save(net.state_dict(), os.path.join(args.save_dir, f'harvest_ys_net_{i_episode}.pth'))