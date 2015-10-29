# -*- coding: utf-8 -*-
#
# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

"""SHA-3/384 cryptographic hash algorithm.

SHA-3/384 belongs to the SHA-3 family of cryptographic hashes, as specified
in `FIPS 202`__.

The hash function produces the 384 bit digest of a message.

    >>> from Crypto.Hash import SHA3_384
    >>>
    >>> h_obj = SHA3_384.new()
    >>> h_obj.update(b'Some data')
    >>> print h_obj.hexdigest()

.. __: http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf
"""

from Crypto.Util.py3compat import bord

from Crypto.Util._raw_api import (load_pycryptodome_raw_lib,
                                  VoidPointer, SmartPointer,
                                  create_string_buffer,
                                  get_raw_buffer, c_size_t,
                                  expect_byte_string)

from Crypto.Hash.keccak import _raw_keccak_lib

class SHA3_384_Hash(object):
    """Class that implements a SHA-3/384 hash
    """

    #: The size of the resulting hash in bytes.
    digest_size = 48

    #: ASN.1 Object ID
    oid = "2.16.840.1.101.3.4.2.9"

    def __init__(self, data=None):
        state = VoidPointer()
        result = _raw_keccak_lib.keccak_init(state.address_of(),
                                             c_size_t(self.digest_size * 2),
                                             0x06)
        if result:
            raise ValueError("Error %d while instantiating SHA-3/384"
                             % result)
        self._state = SmartPointer(state.get(),
                                   _raw_keccak_lib.keccak_destroy)
        if data:
            self.update(data)

    def update(self, data):
        """Continue hashing of a message by consuming the next chunk of data.

        Repeated calls are equivalent to a single call with the concatenation
        of all the arguments. In other words:

           >>> m.update(a); m.update(b)

        is equivalent to:

           >>> m.update(a+b)

        :Parameters:
          data : byte string
            The next chunk of the message being hashed.
        """

        if hasattr(self, "_digest_value"):
            raise TypeError("You can only call 'digest' or 'hexdigest' on this object")

        expect_byte_string(data)
        result = _raw_keccak_lib.keccak_absorb(self._state.get(),
                                               data,
                                               c_size_t(len(data)))
        if result:
            raise ValueError("Error %d while updating SHA-3/384"
                             % result)
        return self

    def digest(self):
        """Return the **binary** (non-printable) digest of the message that has been hashed so far.

        You cannot update the hash anymore after the first call to ``digest``
        (or ``hexdigest``).

        :Return: A byte string of `digest_size` bytes. It may contain non-ASCII
         characters, including null bytes.
        """

        if hasattr(self, "_digest_value"):
            return self._digest_value

        bfr = create_string_buffer(self.digest_size)
        result = _raw_keccak_lib.keccak_squeeze(self._state.get(),
                                                bfr,
                                                c_size_t(self.digest_size))
        if result:
            raise ValueError("Error %d while instantiating SHA-3/384"
                             % result)

        self._digest_value = get_raw_buffer(bfr)
        return self._digest_value

    def hexdigest(self):
        """Return the **printable** digest of the message that has been hashed so far.

        This method does not change the state of the hash object.

        :Return: A string of 2* `digest_size` characters. It contains only
         hexadecimal ASCII digits.
        """

        return "".join(["%02x" % bord(x) for x in self.digest()])

    def new(self, data=None):
        return type(self)(data=data)


def new(data=None):
    """Return a fresh instance of the hash object.

    :Parameters:
       data : byte string
        The very first chunk of the message to hash.
        It is equivalent to an early call to ``update()``.
        Optional.

    :Return: A `SHA3_384_Hash` object
    """
    return SHA3_384_Hash(data=data)

#: The size of the resulting hash in bytes.
digest_size = SHA3_384_Hash.digest_size