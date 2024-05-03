import shutil
import subprocess
from pathlib import Path
import json
from PIL import Image

from ImageDiffMapAnalysis import ImageDiffMapAnalysis


def has_transparency(img):
    if img.info.get("transparency", None) is not None:
        return True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True

    return False


def pimg_decode(pimg_path:Path) -> tuple[Path, Path, Path]:
    psb_decoder_path = Path("./FreeMoteToolkit\\PsbDecompile.exe")
    p = " ".join([f"{psb_decoder_path.absolute()}", f'"{pimg_path.absolute()}"'])
    subprocess.run(p, stdout=subprocess.PIPE)
    base_path = Path(pimg_path.absolute())
    assert base_path.exists()
    return base_path, base_path.with_suffix(".json"), base_path.with_suffix(".resx.json")


# def img_combine(pimg_path, base=None):
#     img_path, json_path, resx_path = pimg_decode(pimg_path)
#     output_prefix = f"./output/{pimg_path.absolute().stem}_{'{}'}.png"
#     with open(json_path) as f:
#         j = json.load(f)
#     with open(resx_path) as f:
#         jr = json.load(f)
#
#     def layer_id2path(lid: str):
#         return pimg_path.parent.joinpath(jr["Resources"][str(lid)])
#
#     width = j["width"]
#     height = j["height"]
#     base_image = None
#     if base is None:
#         base = None
#         probable_bases = []
#         for i in j["layers"]:
#             if i["width"] == width and i["height"] == height:
#                 probable_bases.append(i)
#         if len(probable_bases) == 1:
#             base = probable_bases[0]["layer_id"]
#             base_image = Image.open(layer_id2path(probable_bases[0]["layer_id"]))
#         else:
#             none_trans = []
#             for i in probable_bases:
#                 pb = Image.open(layer_id2path(i["layer_id"]))
#                 if not has_transparency(pb):
#                     none_trans.append((i, pb))
#                 else:
#                     del pb
#             if len(none_trans) == 1:
#                 base_image = none_trans[0][1]
#                 base = none_trans[0][0]["layer_id"]
#             else:
#                 print(f"WARNING: {pimg_path}, won't extract it.")
#                 shutil.rmtree(img_path)
#                 json_path.unlink()
#                 resx_path.unlink()
#                 return False
#     else:
#         base_image = Image.open(layer_id2path(base))
#         base_image.save(output_prefix.format(base))
#     assert base_image is not None and base is not None
#     base_image.save(output_prefix.format(base))
#     for i in j["layers"]:
#         if i["layer_id"] != int(base):
#             pm = Image.open(layer_id2path(str(i["layer_id"])))
#             im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
#             im.paste(pm, (i["left"], i["top"]))
#             new_img = Image.alpha_composite(base_image, im)
#             new_img.save(output_prefix.format(i["layer_id"]))
#             pm.close()
#     shutil.rmtree(img_path)
#     json_path.unlink()
#     resx_path.unlink()


def img_diff_combine(pimg_path, diff_l, image_format=".jpg", quality=60):
    img_path, json_path, resx_path = pimg_decode(pimg_path)
    output_prefix = "./output/{}" + image_format
    with open(json_path) as f:
        j = json.load(f)
    with open(resx_path) as f:
        jr = json.load(f)

    def layer_id2path(lid: str):
        return pimg_path.parent.joinpath(jr["Resources"][str(lid)])

    width = j["width"]
    height = j["height"]
    bases = {}

    def get_image_data_by_name(name):
        for i in j["layers"]:
            if i["name"] == name:
                return Image.open(layer_id2path(i["layer_id"])), (i["left"], i["top"])

    def get_bases(name):
        if bases.get(name) is None:
            bases[name] = get_image_data_by_name(name)[0]
        return bases.get(name)

    for diff in diff_l:
        if diff[2] is not None:
            pm, box = get_image_data_by_name(diff[2])
            im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            im.paste(pm, box)
            new_img = Image.alpha_composite(get_bases(diff[1]), im).convert("RGB")
            new_img.save(output_prefix.format(diff[0]), optimize=True, quality=quality)
            pm.close()
        else:
            new_img = get_bases(diff[1]).convert("RGB")
            new_img.save(output_prefix.format(diff[0]), optimize=True, quality=quality)
    shutil.rmtree(img_path.with_suffix(""))
    json_path.unlink()
    resx_path.unlink()


if __name__ == '__main__':
    Path("./output").mkdir(exist_ok=True)
    # while True:
    #     f = input("File:")
    #     b = input("Base:")
    #     img_combine(f, b)
    # fl = []
    # for p in os.listdir("./pimg"):
    #     if not p.endswith(".pimg"):
    #         continue
    #     if not img_combine(path.join("./pimg", p)):
    #         fl.append(path.join("./pimg", p))
    # for p in fl:
    #     print(p, end=" ")
    #     img_combine(p, input("Base: "))
    diff_data = ImageDiffMapAnalysis("./imagediffmap.csv").data()
    for d in diff_data:
        try:
            img_diff_combine(Path("./pimg").joinpath(d).with_suffix(".pimg"), diff_data[d], quality=85)
        except Exception as e:
            print(e)
