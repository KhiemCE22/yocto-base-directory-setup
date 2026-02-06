# Tắt as-needed triệt để cho recipe gcc
TARGET_LDFLAGS:remove = "-Wl,--as-needed"
export LD_AS_NEEDED = "0"
TARGET_LDFLAGS:append = " -Wl,--no-as-needed"

# Tránh LTO gây loại bỏ quá đà trong link cc1/cc1plus/lto1
INHIBIT_LTO = "1"

# Ép linker resolve phụ thuộc vòng tròn giữa các archive (libbackend.a, libcommon.a, …)
TARGET_LDFLAGS:append = " -Wl,--start-group -Wl,--end-group"

# (Chỉ dùng nếu vẫn không “ăn” các cờ ở trên)
# EXTRA_OEMAKE:append = " LDFLAGS='${LDFLAGS} -Wl,--no-as-needed -Wl,--start-group -Wl,--end-group'"
