from up.utils.new_loader import NewUpLoader

def main():
  up = NewUpLoader().create()
  try:
    up.initialize()
    up.run()
  finally:
    up.stop()

if __name__ == "__main__":
  main()
