import xml.etree.ElementTree as ET
import os
from unittest.mock import patch

import pytest

import src.logic.serializer as serializer


def write_file(path, content=b""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


def test_loesche_pruefanweisung_removes_files_and_overview(tmp_path, monkeypatch):
    # Setup temporary files and paths
    overview = tmp_path / "pruefanweisungen.xml"
    xml_dir = tmp_path / "pruefanweisungen"
    xml_dir.mkdir()
    xml_path = xml_dir / "Test.xml"

    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    img1 = assets_dir / "vorschau.jpg"
    img2 = assets_dir / "eig1.jpg"
    write_file(str(img1), b"img1")
    write_file(str(img2), b"img2")

    # Create pruefanweisung XML with image references
    root = ET.Element('Pruefanweisung')
    ET.SubElement(root, 'Name').text = 'Test'
    ET.SubElement(root, 'VorschauBildPfad').text = str(img1)
    eigenschaften = ET.SubElement(root, 'Eigenschaften')
    eig = ET.SubElement(eigenschaften, 'Eigenschaft')
    bilder = ET.SubElement(eig, 'Bilder')
    bild = ET.SubElement(bilder, 'Bild')
    ET.SubElement(bild, 'BildPfad').text = str(img2)
    tree = ET.ElementTree(root)
    tree.write(str(xml_path), encoding='utf-8', xml_declaration=True)

    # Create overview XML referencing the pruefanweisung xml
    root2 = ET.Element('Pruefanweisungen')
    pw = ET.SubElement(root2, 'Pruefanweisung')
    ET.SubElement(pw, 'Name').text = 'Test'
    ET.SubElement(pw, 'VorschauBildPfad').text = str(img1)
    ET.SubElement(pw, 'PruefanweisungXmlPfad').text = str(xml_path)
    tree2 = ET.ElementTree(root2)
    tree2.write(str(overview), encoding='utf-8', xml_declaration=True)

    # Monkeypatch module-level overview path
    monkeypatch.setattr(serializer, 'pruefanweisungenXmlPfad', str(overview))

    # Ensure files exist
    assert xml_path.exists()
    assert img1.exists()
    assert img2.exists()

    deleted = serializer.loeschePruefanweisung(str(xml_path))

    # Check returned list contains image paths and files removed
    assert str(img1) in deleted
    assert str(img2) in deleted
    assert not xml_path.exists()
    assert not img1.exists()
    assert not img2.exists()

    # Overview should no longer contain the entry
    tree_after = ET.parse(str(overview))
    root_after = tree_after.getroot()
    assert len(root_after.findall('Pruefanweisung')) == 0


def test_loesche_pruefanweisung_handles_missing_overview(tmp_path, monkeypatch):
    # Similar to above but no overview file present
    xml_dir = tmp_path / "pruefanweisungen"
    xml_dir.mkdir()
    xml_path = xml_dir / "Test2.xml"

    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    img = assets_dir / "vorschau2.jpg"
    write_file(str(img), b"img")

    root = ET.Element('Pruefanweisung')
    ET.SubElement(root, 'Name').text = 'Test2'
    ET.SubElement(root, 'VorschauBildPfad').text = str(img)
    tree = ET.ElementTree(root)
    tree.write(str(xml_path), encoding='utf-8', xml_declaration=True)

    # Point overview path to a non-existing file
    monkeypatch.setattr(serializer, 'pruefanweisungenXmlPfad', str(tmp_path / 'nonexistent.xml'))

    # Should not raise, and should remove xml and image
    deleted = serializer.loeschePruefanweisung(str(xml_path))
    assert str(img) in deleted
    assert not xml_path.exists()
    assert not img.exists()
