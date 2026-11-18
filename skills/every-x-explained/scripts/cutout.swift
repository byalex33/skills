// Cut the main subject (e.g. an aircraft) out of a photo onto a transparent background,
// using Apple's Vision framework (the same model as Photos' "Lift subject from background").
// No installs needed on macOS 14+.
//
//   swift cutout.swift <input.jpg|png> <output.png>
//
// Output is cropped to the subject's bounding box plus a small margin.
import Foundation
import Vision
import CoreImage
import CoreImage.CIFilterBuiltins
import UniformTypeIdentifiers

let args = CommandLine.arguments
guard args.count == 3 else {
    FileHandle.standardError.write("usage: swift cutout.swift <input> <output.png>\n".data(using: .utf8)!)
    exit(2)
}
let inURL = URL(fileURLWithPath: args[1]), outURL = URL(fileURLWithPath: args[2])
guard let input = CIImage(contentsOf: inURL, options: [.applyOrientationProperty: true]) else {
    FileHandle.standardError.write("cannot read \(args[1])\n".data(using: .utf8)!); exit(1)
}

let request = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: input, options: [:])
do { try handler.perform([request]) } catch {
    FileHandle.standardError.write("vision failed: \(error)\n".data(using: .utf8)!); exit(1)
}
guard let result = request.results?.first, !result.allInstances.isEmpty else {
    FileHandle.standardError.write("no subject found in \(args[1])\n".data(using: .utf8)!); exit(3)
}

// Keep only the largest instance (the plane, not a tug or a person in front of it).
var best = result.allInstances.first!, bestArea = 0
for idx in result.allInstances {
    if let m = try? result.generateScaledMaskForImage(forInstances: [idx], from: handler) {
        let w = CVPixelBufferGetWidth(m), h = CVPixelBufferGetHeight(m)
        CVPixelBufferLockBaseAddress(m, .readOnly)
        let base = CVPixelBufferGetBaseAddress(m)!.assumingMemoryBound(to: Float32.self)
        let stride = CVPixelBufferGetBytesPerRow(m) / 4
        var area = 0
        for y in Swift.stride(from: 0, to: h, by: 4) { for x in Swift.stride(from: 0, to: w, by: 4) where base[y * stride + x] > 0.5 { area += 1 } }
        CVPixelBufferUnlockBaseAddress(m, .readOnly)
        if area > bestArea { bestArea = area; best = idx }
    }
}
guard let maskBuf = try? result.generateScaledMaskForImage(forInstances: [best], from: handler) else {
    FileHandle.standardError.write("mask failed\n".data(using: .utf8)!); exit(1)
}
let mask = CIImage(cvPixelBuffer: maskBuf)
let blend = CIFilter.blendWithMask()
blend.inputImage = input
blend.backgroundImage = CIImage.empty().cropped(to: input.extent)
blend.maskImage = mask
var out = blend.outputImage!.cropped(to: input.extent)

// crop to subject bounds + 4% margin
let ctx = CIContext()
if let cg = ctx.createCGImage(mask, from: mask.extent) {
    let w = cg.width, h = cg.height
    let data = CFDataGetBytePtr(cg.dataProvider!.data)!
    let bpr = cg.bytesPerRow, bpp = cg.bitsPerPixel / 8
    var minX = w, minY = h, maxX = 0, maxY = 0
    for y in stride(from: 0, to: h, by: 2) { for x in stride(from: 0, to: w, by: 2) where data[y * bpr + x * bpp] > 127 {
        minX = min(minX, x); maxX = max(maxX, x); minY = min(minY, y); maxY = max(maxY, y) } }
    if maxX > minX && maxY > minY {
        let m = Int(Double(max(maxX - minX, maxY - minY)) * 0.04)
        // CoreImage origin is bottom-left
        let r = CGRect(x: max(0, minX - m), y: max(0, h - maxY - m), width: min(w, maxX - minX + 2 * m), height: min(h, maxY - minY + 2 * m))
        out = out.cropped(to: r)
    }
}
do {
    try ctx.writePNGRepresentation(of: out, to: outURL, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
} catch {
    FileHandle.standardError.write("write failed: \(error)\n".data(using: .utf8)!); exit(1)
}
print("ok \(outURL.path)")
