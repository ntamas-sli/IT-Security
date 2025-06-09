#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdint>
#include <stdexcept>
#include <tuple>

class CIFF {
public:
    std::string magic;
    int64_t header_size = 0;
    int64_t content_size = 0;
    int64_t width = 0;
    int64_t height = 0;
    std::string caption;
    std::vector<std::string> tags;
    std::vector<std::tuple<uint8_t, uint8_t, uint8_t>> pixels;
    bool is_valid = true;

    static CIFF parse_ciff(const std::string& path) {
        CIFF ciff;
        std::ifstream file(path, std::ios::binary);
        if (!file) {
            ciff.is_valid = false;
            return ciff;
        }

        try {
            // Read magic
            char magic_buf[4];
            file.read(magic_buf, 4);
            if (file.gcount() != 4) throw std::runtime_error("Invalid magic size");
            ciff.magic = std::string(magic_buf, 4);
            if (ciff.magic != "CIFF") throw std::runtime_error("Magic mismatch");

            // Read header size
            ciff.header_size = read_int64(file);
            if (ciff.header_size < 38) throw std::runtime_error("Invalid header size");

            // Read content size
            ciff.content_size = read_int64(file);
            if (ciff.content_size < 0) throw std::runtime_error("Invalid content size");

            // Read width and height
            ciff.width = read_int64(file);
            ciff.height = read_int64(file);
            if (ciff.width < 0 || ciff.height < 0) throw std::runtime_error("Invalid dimensions");

            // Validate content size
            if (ciff.content_size != ciff.width * ciff.height * 3)
                throw std::runtime_error("Content size mismatch");

            // Read caption
            char ch;
            while (file.get(ch)) {
                if (ch == '\n') break;
                ciff.caption += ch;
            }
            if (file.eof()) throw std::runtime_error("Unexpected EOF in caption");

            // Read tags
            int64_t bytes_read = 36 + ciff.caption.size() + 1;
            std::string tag;
            while (bytes_read < ciff.header_size) {
                if (!file.get(ch)) throw std::runtime_error("Unexpected EOF in tags");
                bytes_read++;
                if (ch == '\n') throw std::runtime_error("Newline in tag not allowed");
                tag += ch;
                if (ch == '\0') {
                    ciff.tags.push_back(tag);
                    tag.clear();
                }
                if (bytes_read == ciff.header_size && ch != '\0')
                    throw std::runtime_error("Header must end with null terminator");
            }

            // Validate tag endings
            for (const auto& t : ciff.tags) {
                if (t.empty() || t.back() != '\0')
                    throw std::runtime_error("Tag must end with null character");
            }

            // Read pixels
            int64_t pixel_bytes = 0;
            while (pixel_bytes < ciff.content_size) {
                uint8_t rgb[3];
                file.read(reinterpret_cast<char*>(rgb), 3);
                if (file.gcount() != 3) throw std::runtime_error("Incomplete pixel");
                ciff.pixels.emplace_back(rgb[0], rgb[1], rgb[2]);
                pixel_bytes += 3;
            }

            // Check for extra bytes
            if (file.get(ch)) throw std::runtime_error("Extra data after pixels");

        } catch (...) {
            ciff.is_valid = false;
        }

        return ciff;
    }

private:
    static int64_t read_int64(std::ifstream& file) {
        int64_t val;
        file.read(reinterpret_cast<char*>(&val), 8);
        if (file.gcount() != 8) throw std::runtime_error("Failed to read int64");
        return val;
    }
};

extern "C" __declspec(dllexport)
CIFF* parse(const char* filepath) {
    std::string path(filepath);

    CIFF result = CIFF::parse_ciff(path);

    CIFF* result_ptr = new CIFF(result);

    return result_ptr;
}