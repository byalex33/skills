// Turn a circuit map (any style: turn numbers, labels, arrows, grey alternate layouts)
// into a clean track line of one standard width on a transparent background.
//
//   swiftc -O trackline.swift -o trackline && ./trackline in.png out.png [--invert-light] [--close N] [--prune N]
// --close bridges gaps but leaves spurs; raise --prune (spur length in px at 1000 px, default 35) with it.
//
// Steps: draw onto white at 1000 px on the long side -> mask the dark pixels (the track line)
// -> erode until the thin strokes (digits, circle outlines, text) vanish -> keep the largest
// connected piece -> thin it to its core -> dilate to one fixed width -> crop, write black PNG.
// --invert-light: use for maps that draw the track light on a dark/coloured background.
import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let a = CommandLine.arguments
guard a.count >= 3, let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil),
      let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    FileHandle.standardError.write("usage: trackline in.png out.png [--invert-light]\n".data(using: .utf8)!); exit(2)
}
let invert = a.contains("--invert-light")
let S = 1000.0
let sc = S / Double(max(img.width, img.height))
let W = Int(Double(img.width) * sc), H = Int(Double(img.height) * sc)
var px = [UInt8](repeating: 255, count: W * H * 4)
let cs = CGColorSpaceCreateDeviceRGB()
let ctx = CGContext(data: &px, width: W, height: H, bitsPerComponent: 8, bytesPerRow: W * 4, space: cs,
                    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
ctx.interpolationQuality = .high
ctx.draw(img, in: CGRect(x: 0, y: 0, width: W, height: H))

// 1. mask: dark, unsaturated pixels (black track); grey alternates and red arrows drop out.
var m = [Bool](repeating: false, count: W * H)
for i in 0..<(W * H) {
    let r = Int(px[i*4]), g = Int(px[i*4+1]), b = Int(px[i*4+2])
    let lum = (r * 299 + g * 587 + b * 114) / 1000
    let sat = max(r, g, b) - min(r, g, b)
    m[i] = invert ? (lum > 200 && sat < 40) : (lum < 150 && sat < 60)
}
if invert { // light track on a background: also drop the outer white margin
    var seen = [Bool](repeating: false, count: W * H); var st = [Int]()
    for x in 0..<W { st.append(x); st.append((H-1)*W + x) }
    for y in 0..<H { st.append(y*W); st.append(y*W + W-1) }
    while let i = st.popLast() { if seen[i] || !m[i] { continue }; seen[i] = true; m[i] = false
        let x = i % W, y = i / W
        if x > 0 { st.append(i-1) }; if x < W-1 { st.append(i+1) }; if y > 0 { st.append(i-W) }; if y < H-1 { st.append(i+W) } }
}

func erode(_ m: [Bool]) -> [Bool] {
    var o = m
    for y in 0..<H { for x in 0..<W where m[y*W+x] {
        if x == 0 || y == 0 || x == W-1 || y == H-1 || !m[y*W+x-1] || !m[y*W+x+1] || !m[(y-1)*W+x] || !m[(y+1)*W+x] { o[y*W+x] = false } } }
    return o
}
func dilate(_ m: [Bool], _ r: Int) -> [Bool] {
    var o = m; let r2 = r * r
    var offs = [(Int, Int)](); for dy in -r...r { for dx in -r...r where dx*dx + dy*dy <= r2 { offs.append((dx, dy)) } }
    for y in 0..<H { for x in 0..<W where m[y*W+x] {
        if x > 0 && y > 0 && x < W-1 && y < H-1 && m[y*W+x-1] && m[y*W+x+1] && m[(y-1)*W+x] && m[(y+1)*W+x] { continue }
        for (dx, dy) in offs { let nx = x+dx, ny = y+dy; if nx >= 0 && ny >= 0 && nx < W && ny < H { o[ny*W+nx] = true } } } }
    return o
}
/// Connected components (8-neighbour). Returns label per pixel and size per label.
func components(_ m: [Bool]) -> ([Int32], [Int]) {
    var lab = [Int32](repeating: 0, count: W * H); var sizes = [0]; var cur: Int32 = 0
    for s in 0..<(W*H) where m[s] && lab[s] == 0 {
        cur += 1; var n = 0; var st = [s]; lab[s] = cur
        while let i = st.popLast() { n += 1; let x = i % W, y = i / W
            for dy in -1...1 { for dx in -1...1 where dx != 0 || dy != 0 {
                let nx = x+dx, ny = y+dy; if nx < 0 || ny < 0 || nx >= W || ny >= H { continue }
                let j = ny*W+nx; if m[j] && lab[j] == 0 { lab[j] = cur; st.append(j) } } } }
        sizes.append(n)
    }
    return (lab, sizes)
}
/// Bounding-box diagonal of each component: the track spans the map, a filled marker disk does not.
func extents(_ lab: [Int32], _ n: Int) -> [Double] {
    var x0 = [Int](repeating: W, count: n), x1 = [Int](repeating: -1, count: n)
    var y0 = [Int](repeating: H, count: n), y1 = [Int](repeating: -1, count: n)
    for y in 0..<H { for x in 0..<W { let l = Int(lab[y*W+x]); if l == 0 { continue }
        x0[l] = min(x0[l], x); x1[l] = max(x1[l], x); y0[l] = min(y0[l], y); y1[l] = max(y1[l], y) } }
    return (0..<n).map { x1[$0] < 0 ? 0 : hypot(Double(x1[$0]-x0[$0]), Double(y1[$0]-y0[$0])) }
}
/// The component with the widest extent ("the track"), and its pixel count.
func largest(_ m: [Bool]) -> ([Bool], Int) {
    let (lab, sz) = components(m); guard sz.count > 1 else { return (m, 0) }
    let ex = extents(lab, sz.count)
    let b = sz.indices.dropFirst().max { ex[$0] < ex[$1] }!
    return (lab.map { Int($0) == b }, sz[b])
}
let count = { (m: [Bool]) in m.reduce(0) { $0 + ($1 ? 1 : 0) } }

// 2. fill small, compact enclosed white regions (turn-number circles sitting on the track),
//    so they bridge the line instead of cutting it.
do {
    let (lab, sz) = components(m.map { !$0 })
    var minX = [Int](repeating: W, count: sz.count), maxX = [Int](repeating: 0, count: sz.count)
    var minY = [Int](repeating: H, count: sz.count), maxY = [Int](repeating: 0, count: sz.count)
    var border = [Bool](repeating: false, count: sz.count)
    for y in 0..<H { for x in 0..<W { let l = Int(lab[y*W+x]); if l == 0 { continue }
        minX[l] = min(minX[l], x); maxX[l] = max(maxX[l], x); minY[l] = min(minY[l], y); maxY[l] = max(maxY[l], y)
        if x == 0 || y == 0 || x == W-1 || y == H-1 { border[l] = true } } }
    var fill = [Bool](repeating: false, count: sz.count)
    for l in 1..<sz.count where !border[l] && sz[l] < 3000 {
        let bw = maxX[l]-minX[l]+1, bh = maxY[l]-minY[l]+1
        if Double(min(bw, bh)) / Double(max(bw, bh)) > 0.6 && Double(sz[l]) / Double(bw*bh) > 0.45 { fill[l] = true }
    }
    for i in 0..<(W*H) where lab[i] != 0 && fill[Int(lab[i])] { m[i] = true }
}

// 2b. --close N: bridge gaps up to ~2N px (marker circles that cut the line), by dilate then erode.
if let ci = a.firstIndex(of: "--close"), ci + 1 < a.count, let n = Int(a[ci + 1]), n > 0 {
    m = dilate(m, n); for _ in 0..<n { m = erode(m) }
}

// 3. half-width k of the track line: erode until the biggest piece shrinks away.
var k = 0
do { var e = m; let base = largest(m).1
     while k < 40 { let n = erode(e); if largest(n).1 < max(150, base / 30) { break }; e = n; k += 1 } }
// 4. opening (erode then dilate by ~half the width) drops thin text, outlines and digits;
//    keep every piece at least 5% the size of the biggest (the track can be cut by a label).
let open = max(1, k / 2 + 1)
var c = m; for _ in 0..<open { c = erode(c) }; c = dilate(c, open)
do { let (lab, sz) = components(c); let ex = extents(lab, sz.count); let big = ex.max() ?? 0
     c = lab.map { $0 != 0 && ex[Int($0)] * 5 >= big } }   // keep track pieces cut by a label
// 5. Zhang-Suen thinning to a 1 px centre line.
var t = c
func nb(_ i: Int) -> [Bool] { [t[i-W], t[i-W+1], t[i+1], t[i+W+1], t[i+W], t[i+W-1], t[i-1], t[i-W-1]] }
var changed = true
while changed { changed = false
    for pass in 0..<2 { var del = [Int]()
        for y in 1..<(H-1) { for x in 1..<(W-1) { let i = y*W+x; if !t[i] { continue }
            let p = nb(i); let b = p.reduce(0) { $0 + ($1 ? 1 : 0) }; if b < 2 || b > 6 { continue }
            var a = 0; for q in 0..<8 where !p[q] && p[(q+1)%8] { a += 1 }; if a != 1 { continue }
            if pass == 0 { if p[0] && p[2] && p[4] { continue }; if p[2] && p[4] && p[6] { continue } }
            else { if p[0] && p[2] && p[6] { continue }; if p[0] && p[4] && p[6] { continue } }
            del.append(i) } }
        if !del.isEmpty { changed = true; for i in del { t[i] = false } } } }
// 6. keep the main centre line; prune short spurs left by circles and arrows.
t = largest(t).0
let prune = a.firstIndex(of: "--prune").flatMap { $0 + 1 < a.count ? Int(a[$0 + 1]) : nil } ?? 35
for _ in 0..<prune { var ends = [Int]()
    for y in 1..<(H-1) { for x in 1..<(W-1) { let i = y*W+x; if t[i] && nb(i).filter({ $0 }).count <= 1 { ends.append(i) } } }
    if ends.isEmpty { break }; for i in ends { t[i] = false } }
let out = dilate(t, 9)             // 19 px line at 1000 px = ~1.9% of the long side

// 5. crop + write black on transparent
var minX = W, minY = H, maxX = 0, maxY = 0
for y in 0..<H { for x in 0..<W where out[y*W+x] { minX = min(minX, x); maxX = max(maxX, x); minY = min(minY, y); maxY = max(maxY, y) } }
let pad = 12; minX = max(0, minX-pad); minY = max(0, minY-pad); maxX = min(W-1, maxX+pad); maxY = min(H-1, maxY+pad)
let OW = maxX - minX + 1, OH = maxY - minY + 1
var o = [UInt8](repeating: 0, count: OW * OH * 4)
for y in 0..<OH { for x in 0..<OW where out[(y+minY)*W + x+minX] { let i = (y*OW+x)*4; o[i] = 17; o[i+1] = 17; o[i+2] = 17; o[i+3] = 255 } }
let octx = CGContext(data: &o, width: OW, height: OH, bitsPerComponent: 8, bytesPerRow: OW * 4, space: cs,
                     bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
let dst = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[2]) as CFURL, UTType.png.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(dst, octx.makeImage()!, nil); CGImageDestinationFinalize(dst)
print("ok \(a[2]) halfwidth=\(k) \(OW)x\(OH)")
