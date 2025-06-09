#include "CIFF.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>

using namespace std;

extern "C" {

CIFF CIFF::parse_ciff_file(const string& file_path) {
    CIFF ciff;
    size_t bytes_read = 0;

    try {
        ifstream file(file_path, ios::binary);
        if (!file) throw runtime_error("Cannot open file");

        char magic_buf[4];
        file.read(magic_buf, 4);
        if (file.gcount() != 4) throw runtime_error("Magic bytes missing");
        ciff.magic = string(magic_buf, 4);
        bytes_read += 4;

        if (ciff.magic != "CIFF") throw runtime_error("Magic does not match");

        auto read_int64 = [&](int64_t& target) {
            char buf[8];
            file.read(buf, 8);
            if (file.gcount() != 8) throw runtime_error("Failed to read int64");
            target = *reinterpret_cast<int64_t*>(buf);
            bytes_read += 8;
        };

        read_int64(ciff.header_size);
        if (ciff.header_size < 38 || ciff.header_size > INT64_MAX)
            throw runtime_error("Invalid header size");

        read_int64(ciff.content_size);
        if (ciff.content_size < 0)
            throw runtime_error("Invalid content size");

        read_int64(ciff.width);
        if (ciff.width <= 0)
            throw runtime_error("Invalid width");

        read_int64(ciff.height);
        if (ciff.height <= 0)
            throw runtime_error("Invalid height");

        if (ciff.content_size != ciff.width * ciff.height * 3)
            throw runtime_error("Content size does not match dimensions");

        // Read caption
        char ch;
        while (file.get(ch) && ch != '\n') {
            ciff.caption += ch;
            bytes_read++;
        }
        if (file.eof()) throw runtime_error("Caption not terminated");
        bytes_read++; // for '\n'

        // Read tags
        string tag;
        while (bytes_read < static_cast<size_t>(ciff.header_size)) {
            file.get(ch);
            if (file.eof()) throw runtime_error("Unexpected EOF while reading tags");
            bytes_read++;
            if (ch == '\n') throw runtime_error("Tags must not contain newline");
            tag += ch;
            if (ch == '\0') {
                ciff.tags.push_back(tag);
                tag.clear();
            }
        }
        if (tag.size() > 0) throw runtime_error("Header must end with null");

        for (const auto& t : ciff.tags) {
            if (t.back() != '\0') throw runtime_error("Tag must end with null");
        }

        // Read pixels
        size_t pixel_count = ciff.width * ciff.height;
        for (size_t i = 0; i < pixel_count; ++i) {
            char rgb[3];
            file.read(rgb, 3);
            if (file.gcount() != 3) throw runtime_error("Failed to read pixel");
            ciff.pixels.emplace_back(
                static_cast<uint8_t>(rgb[0]),
                static_cast<uint8_t>(rgb[1]),
                static_cast<uint8_t>(rgb[2])
            );
            bytes_read += 3;
        }

        // Check for extra data
        char extra;
        if (file.get(extra)) throw runtime_error("Extra data found");

    } catch (exception& e) {
        ciff.is_valid = false;
        cerr << "Error parsing CIFF: " << e.what() << endl;
    }

    return ciff;
}

}