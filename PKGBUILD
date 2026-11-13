# Build & install from a checkout of the repository:  makepkg -si
pkgname=bootrepair
pkgver=0.3.1
pkgrel=1
pkgdesc="Diagnose and repair Windows installations that do not start (GTK4/libadwaita)"
arch=('any')
url="https://github.com/Bot320/bootrepair"
license=('GPL-3.0-or-later')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'util-linux' 'polkit')
optdepends=('ntfs-3g: read fallback for damaged NTFS volumes; needed to discard a hibernation image'
            'cryptsetup: unlock BitLocker volumes with the recovery key'
            'smartmontools: disk health (S.M.A.R.T.) check'
            'efibootmgr: check and repair the firmware boot entries')

check() {
  cd "$startdir"
  python -m unittest discover -s tests
}

package() {
  cd "$startdir"
  install -d "$pkgdir/usr/lib/bootrepair"
  cp -r --no-preserve=ownership bootrepair "$pkgdir/usr/lib/bootrepair/"
  find "$pkgdir/usr/lib/bootrepair" -name __pycache__ -prune -exec rm -rf {} +
  install -Dm755 bootrepair-helper "$pkgdir/usr/lib/bootrepair/bootrepair-helper"
  install -Dm755 data/bootrepair.sh "$pkgdir/usr/bin/bootrepair"
  ln -s /usr/lib/bootrepair/bootrepair-helper "$pkgdir/usr/bin/bootrepair-helper"
  install -Dm644 data/io.github.bootrepair.desktop "$pkgdir/usr/share/applications/io.github.bootrepair.desktop"
  install -Dm644 data/icons/hicolor/scalable/apps/io.github.bootrepair.svg \
    "$pkgdir/usr/share/icons/hicolor/scalable/apps/io.github.bootrepair.svg"
  install -Dm644 data/icons/hicolor/symbolic/apps/io.github.bootrepair-symbolic.svg \
    "$pkgdir/usr/share/icons/hicolor/symbolic/apps/io.github.bootrepair-symbolic.svg"
  install -Dm644 data/io.github.bootrepair.policy "$pkgdir/usr/share/polkit-1/actions/io.github.bootrepair.policy"
  python -m compileall -q -d /usr/lib/bootrepair "$pkgdir/usr/lib/bootrepair/bootrepair"
}
