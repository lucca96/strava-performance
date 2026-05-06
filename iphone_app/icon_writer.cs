using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;

public static class IconWriter
{
    public static void WriteIcon(string path, int size)
    {
        using (var bmp = new Bitmap(size, size))
        using (var g = Graphics.FromImage(bmp))
        using (var surface = new SolidBrush(Color.FromArgb(22, 22, 22)))
        using (var border = new Pen(Color.FromArgb(36, 255, 255, 255), Math.Max(2f, size * 0.008f)))
        using (var textBrush = new SolidBrush(Color.FromArgb(240, 237, 232)))
        using (var orangeBrush = new SolidBrush(Color.FromArgb(232, 98, 42)))
        using (var orangePen = new Pen(Color.FromArgb(232, 98, 42), Math.Max(8f, size * 0.035f)))
        using (var font = new Font("Arial", size * 0.30f, FontStyle.Bold, GraphicsUnit.Pixel))
        using (var sf = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center })
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.Clear(Color.FromArgb(12, 12, 12));

            var outer = new RectangleF(8f, 8f, size - 16f, size - 16f);
            float radius = size * 0.18f;
            float diam = radius * 2f;

            using (var pathObj = new GraphicsPath())
            {
                pathObj.AddArc(outer.X, outer.Y, diam, diam, 180, 90);
                pathObj.AddArc(outer.Right - diam, outer.Y, diam, diam, 270, 90);
                pathObj.AddArc(outer.Right - diam, outer.Bottom - diam, diam, diam, 0, 90);
                pathObj.AddArc(outer.X, outer.Bottom - diam, diam, diam, 90, 90);
                pathObj.CloseFigure();
                g.FillPath(surface, pathObj);
                g.DrawPath(border, pathObj);
            }

            orangePen.StartCap = LineCap.Round;
            orangePen.EndCap = LineCap.Round;

            var textRect = new RectangleF(0f, size * 0.12f, size, size * 0.46f);
            g.DrawString("FL", font, textBrush, textRect, sf);
            g.DrawLine(orangePen, size * 0.20f, size * 0.76f, size * 0.72f, size * 0.62f);
            g.FillEllipse(orangeBrush, size * 0.70f, size * 0.56f, size * 0.12f, size * 0.12f);

            Directory.CreateDirectory(Path.GetDirectoryName(path));
            bmp.Save(path);
        }
    }
}
