@nb.jit
def find_local_envelop(minmax, arr, winsize, start=0):
    count = arr.shape[0]
    end = min(count, start + winsize + 1)
    rv = arr[start]
    rp = start
    p = start + 1
    while p < end:
        v = arr[p]
        if ((minmax == 1) and (v >= rv)) or ((minmax == -1) and (v <= rv)):
            rv = v
            rp = p
            end = min(count, rp + winsize + 1)
        p += 1
    return rp


@nb.jit
def find_envelop(arr, winsize):
    result = np.zeros(arr.shape[0], dtype=np.int32)
    maxp = find_local_envelop(1, arr, winsize)
    minp = find_local_envelop(-1, arr, winsize)
    mode, pos = (-1, maxp) if maxp < minp else (1, minp)
    prev = -1
    while pos != prev:
        prev, pos = pos, find_local_envelop(mode, arr, winsize, pos)
        mode = -1 if mode == 1 else 1
        result[prev] = mode
        if arr.shape[0] - prev < winsize:
            break
    return result


@nb.jit
def rfind_local_envelop(minmax, arr, winsize):
    count = arr.shape[0]
    end = max(-1, count - winsize)
    rv = arr[0]
    rp = count - 1
    p = 1
    while p > end:
        v = arr[p]
        if ((minmax == 1) and (v >= rv)) or ((minmax == -1) and (v <= rv)):
            rv = v
            rp = p
            end = max(-1, rp + winsize)
        p -= 1
    return rp


def plot_peak(ax, arr, winsize, color, gap):
    env = find_envelop(arr, winsize)
    sig_high = np.full_like(env, np.nan, dtype=np.float32)
    sig_high[env == 1] = arr[env == 1] + gap
    ax.plot(sig_high, 'v', markersize=3, color=color)
    sig_low = np.full_like(env, np.nan, dtype=np.float32)
    sig_low[env == -1] = arr[env == -1] - gap
    ax.plot(sig_low, '^', markersize=3, color=color)


def plot_envelop(arr):
    fig, ax = plt.subplots(1, 1, figsize=(16, 3))
    ax.plot(arr, '-', linewidth=1)
    gap = arr.max() - arr.min()
    plot_peak(ax, arr, 4, 'g', gap * 0.04)
    plot_peak(ax, arr, 60, 'r', gap * 0.08)
    plt.grid(True)
    plt.show()


def plot_envelop_multiline(arr, minspergraph=60):
    count = arr.shape[0]
    grcount = (count + minspergraph - 1) // minspergraph
    fig, axs = plt.subplots(grcount, 1, figsize=(16, grcount*3))
    for axi in range(grcount):
        ax = axs[axi]
        a = arr[axi*minspergraph:(axi+1)*minspergraph]
        gap = a.max() - a.min()
        ax.plot(a, '.-', linewidth=1)
        plot_peak(ax, a, 3, 'g', gap * 0.04)
        plot_peak(ax, a, 60, 'r', gap * 0.08)
        ax.grid(True)
    plt.show()


key = 250227
plot_envelop(dict_csv[key][:, 4])
# plot_envelop_multiline(dict_csv[key][:, 4], 120)
