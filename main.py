from cvs import CloneVersionSystem


def main():
    cvs = CloneVersionSystem()
    try:
        cvs.run()
    except KeyboardInterrupt:
        if cvs.cvs_active:
            cvs.save_in_saver()
        raise


if __name__ == '__main__':
    main()
