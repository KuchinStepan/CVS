from cvs import CloneVersionSystem


def main():
    cvs = CloneVersionSystem()
    cvs.run()
    # try:
    #     cvs.run()
    # except KeyboardInterrupt:
    #     cvs.save_in_saver()


if __name__ == '__main__':
    main()
