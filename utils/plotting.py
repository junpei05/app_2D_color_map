def custom_ncmap(name, n):
    import matplotlib.pyplot as plt
    base = plt.get_cmap(name)
    return [base(i / (n - 1)) for i in range(n)]
