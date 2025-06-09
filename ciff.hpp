#ifndef CIFF_HPP
#define CIFF_HPP

#include <string>
#include <vector>
#include <tuple>

class CIFF {
public:
    bool is_valid = true;
    std::string magic = "CIFF";
    int64_t header_size = 0;
    int64_t content_size = 0;
    int64_t width = 0;
    int64_t height = 0;
    std::string caption = "";
    std::vector<std::string> tags;
    std::vector<std::tuple<uint8_t, uint8_t, uint8_t>> pixels;

    static CIFF parse_ciff_file(const std::string& file_path);
};

#endif
