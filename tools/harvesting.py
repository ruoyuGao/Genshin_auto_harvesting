from yolox2dqn import Predictor
import utils
import models
import environment
from loguru import logger
import os


def main(exp,args):
    model=exp.get_model()
    item_list=environment.ItemCheck().item_list
    #change file name here if you need
    file_name=''
    if args.trt:
        assert not args.fuse, "TensorRT model is not support model fusing!"
        if args.ckpt is None:
            trt_file = os.path.join(file_name, "model_trt.pth")
        else:
            trt_file = args.ckpt
        assert os.path.exists(
            trt_file
        ), "TensorRT model is not found!\n Run python3 tools/trt.py first!"
        model.head.decode_in_inference = False
        decoder = model.head.decode_outputs
        logger.info("Using TensorRT to inference")
    else:
        trt_file = None
        decoder = None
    
    predictor=Predictor(model,exp,item_list,trt_file,decoder,args.device,args.fp16,args.legacy)
    #agent=DQN()
    env=environment(predictor)

    state=env.reset()

    for i in range(1000):
        action=agent(state)
        state,reward,done=env.step(action)


if __name__ == "__main__":
    args = make_parser().parse_args()
    exp = get_exp(args.exp_file, args.name)

    main(exp, args)
